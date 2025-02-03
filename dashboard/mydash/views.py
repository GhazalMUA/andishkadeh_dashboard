from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from mydash.models import ResearchCenter, Continent, Region, ResearchArea, Order, OrderDetail, Status, OrderResult
from django.contrib.auth.models import User
from .tasks import  process_bot
from .utils import generate_query
from datetime import datetime
import os
from django.conf import settings
from .tasks import process_bot
from mydash.bot.config import MY_IGNORED_LIST, COUNTRY_LIST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib import messages
def signup(request):
    """Handle user signup."""
    print("Rendering signup page")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created! You can now log in.")
            print("Redirecting to login page...")

            return redirect(reverse("login"))  # Redirect to the login page after signup
        else:
            messages.error(request, "There was an error with your signup.")
    else:
        form = UserCreationForm()
    
    return render(request, "signup.html", {"form": form})

def login_view(request):
    """Handle user login."""
    print("Rendering login page")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You are logged in.")
            print("Redirecting to: ", reverse("choose-step"))
            return redirect (reverse("choose-step"))  # Redirect to the 'choose-step' page after login
        else:
            messages.error(request, "Invalid username or password.")
            
    else:
        form = AuthenticationForm()
    
    return render(request, "login.html", {"form": form})

def choose_step(request):
    # This view will render the page with the two buttons (Choose manually, Choose by filtering)
    return render(request, 'choose_step.html')

def choose_manually(request):
    # This view will handle the manual selection and render the page for selecting research centers
    research_centers = ResearchCenter.objects.all()
    
    if request.method == "POST":
        selected_centers = request.POST.getlist('research_centers')  # Get selected research centers
        if selected_centers:
            # Create a new order and save it
            order = Order.objects.create(
                user=request.user,  # Assuming the user is logged in
                keyword="",
                final_status=Status.objects.get(name="Pending")  # Example status
            )
            # Save the selected research centers in OrderDetail
            for center_id in selected_centers:
                research_center = ResearchCenter.objects.get(id=center_id)
                OrderDetail.objects.create(
                    order=order,
                    research_center=research_center,
                    query=""  # Leave this empty for now, it will be filled later when the keyword is provided(in additional_data we will get the keyword from the user.)
                )
            order.save()    
            return redirect('choose_keyword_time', order_id=order.id)  # Redirect to next page for choosing keyword and datetime.
    
    return render(request, 'choose_manually.html', {'research_centers': research_centers})

def choose_by_filter(request):
    continents = Continent.objects.all()
    regions = Region.objects.all()
    research_areas = ResearchArea.objects.all()

    if request.method == "POST":
        selected_continent = request.POST.get('continent')
        selected_region = request.POST.get('region')
        selected_research_area = request.POST.get('research_area')

        order = Order.objects.create(
            user=request.user,  # Assuming the user is logged in
            keyword="",
            final_status=Status.objects.get(name="Pending")
        )

        # Filter the research centers based on selected filters
        filtered_centers = ResearchCenter.objects.filter(
            continent__name=selected_continent,
            region__name=selected_region,
        )

        if selected_research_area:
            filtered_centers = filtered_centers.filter(
                research_areas__name=selected_research_area
            )

        if filtered_centers.exists():
            # Save filtered centers
            for center in filtered_centers:
                OrderDetail.objects.create(
                    order=order,
                    research_center=center,
                    query=""
                )

            return redirect('choose_keyword_time', order_id=order.id)  # Redirect to next page
        else:
            return render(request, 'choose_by_filter.html', {
                'continents': continents,
                'regions': regions,
                'research_areas': research_areas,
                'error': "No research centers match your criteria."
            })

    return render(request, 'choose_by_filter.html', {
        'continents': continents,
        'regions': regions,
        'research_areas': research_areas
    })

def choose_keyword_time(request, order_id):
    """Handle keyword and time range or custom date selection for an order."""
    
    # Retrieve the order object
    order = Order.objects.get(id=order_id)

    if request.method == 'POST':
        keyword = request.POST.get('keyword')  # Get the keyword input from the user
        selected_time_range = request.POST.get('time_range')  # Get the selected time range
        start_date = request.POST.get('start_date')  # Get custom start date
        end_date = request.POST.get('end_date')  # Get custom end date
        
        # Ensure that both time range and custom date range are not selected simultaneously
        if selected_time_range and (start_date or end_date):
            return render(request, 'choose_keyword_time.html', {'order': order, 'error': "Please select either a time range or custom date range, not both."})

        if selected_time_range:  # Time range is selected
            order.time_range = selected_time_range
            order.start_date = None
            order.end_date = None
            order.save()

        elif start_date and end_date:  # Custom date range is selected
            try:
                # Validate the custom date range
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                
                # Ensure the start_date is not after the end_date
                if start_date > end_date:
                    return render(request, 'choose_keyword_time.html', {'order': order, 'error': "Start date cannot be after end date."})
                
                # Save custom date range to the order
                order.start_date = start_date
                order.end_date = end_date
                order.time_range = None  # Remove time_range if custom dates are selected
                order.save()
        
            except ValueError:
                return render(request, 'choose_keyword_time.html', {'order': order, 'error': "Invalid date format. Please use YYYY-MM-DD."})

        # Proceed with query generation and saving order details
        order_detail = OrderDetail.objects.get(order=order)
        research_center = order_detail.research_center
        query = generate_query(keyword=keyword, website=research_center.website)
        order_detail.query = query
        
        # Save the order detail
        order_detail.save()
        time_data = {
            'start_date': order.start_date,
            'end_date': order.end_date,
            'time_range': order.time_range
        }
        
        if keyword:
            order.keyword = keyword  # Save the chosen keyword
        order.save()
        
        return redirect('order_summary', order_id=order_id)

    return render(request, 'choose_keyword_time.html', {'order': order})

def order_summary(request, order_id):
    print("Entering order_summary view...")
    try:
        
        order = Order.objects.get(id=order_id)
        print(f"Order found: {order}")
        order_details = OrderDetail.objects.filter(order=order)
        print(f"Order details: {order_details}")
        order_result = OrderResult.objects.filter(order_detail__order=order).first()
        print(f"Order result: {order_result}")

        if request.method == "POST":
            print("POST request received.")
            query = order_details.first().query  # Assuming all order details have the same query
            ignore_list = MY_IGNORED_LIST  # Add your ignore list here
            country_list = COUNTRY_LIST  # Add your country list here
            start_date = order.start_date
            end_date = order.end_date

            print(f"Order ID: {order.id}")
            print(f"Query: {query}")
            print(f"Ignore List: {ignore_list}")
            print(f"Country List: {country_list}")
            print(f"Start Date: {start_date}, End Date: {end_date}")

            # Trigger the Celery task and pass the required arguments
            print("Triggering Celery task...")
            process_bot.delay(
                order.id,
                query,
                order.time_range,  # This will be used if no custom range is provided
                start_date,
                end_date,
                ignore_list,
                country_list
            )
            print("Celery task triggered.")

            return redirect('order_waiting', order_id=order.id)

        return render(request, 'order_summary.html', {'order': order, 'order_details': order_details})

    except Exception as e:
        print(f"Error in order_summary view: {e}")
        raise
    

def remove_order_detail(request, order_detail_id):
    order_detail = OrderDetail.objects.get(id=order_detail_id)
    order_detail.delete()
    return redirect('order_summary', order_id=order_detail.order.id)

def order_waiting(request, order_id):
    order = Order.objects.get(id=order_id)
    order_details = OrderDetail.objects.filter(order=order)
    order_result = OrderResult.objects.filter(order_detail__order=order).first()

    if order_result and order_result.is_processed:
        # The result is ready, show it to the user
        return render(request, 'order_result.html', {'order': order, 'order_result': order_result})
    
    # Otherwise, show a "waiting" message
    return render(request, 'order_waiting.html', {'order': order, 'order_details': order_details})

def show_result(request, order_id):
    # Assume you have already fetched the result file path using order_id
    result_file_path = os.path.join(settings.MEDIA_ROOT, 'results', f'order_{order_id}_timestamp.xlsx')
    
    if os.path.exists(result_file_path):
        result_file_url = os.path.join(settings.MEDIA_URL, 'results', f'order_{order_id}_timestamp.xlsx')
        return render(request, 'show_result.html', {'order_id': order_id, 'result_file_url': result_file_url})
    else:
        return HttpResponse("Result file not found", status=404)
    
def edit_order_detail(request):
    pass




# def order_summary(request, order_id):
#     print("Entering order_summary view...")
#     try:
#         order = Order.objects.get(id=order_id)
#         print(f"Order found: {order}")
#         order_details = OrderDetail.objects.filter(order=order)
#         print(f"Order details: {order_details}")
#         order_result = OrderResult.objects.filter(order_detail__order=order).first()
#         print(f"Order result: {order_result}")

#         if request.method == "POST":
#             print("POST request received.")
#             query = order_details.first().query  # Assuming all order details have the same query
#             time_data = {
#                 'start_date': order.start_date,
#                 'end_date': order.end_date,
#                 'time_range': order.time_range
#             }
#             ignore_list = MY_IGNORED_LIST
#             country_list = COUNTRY_LIST

#             print(f"Order ID: {order.id}")
#             print(f"Query: {query}")
#             print(f"Time Data: {time_data}")
#             print(f"Ignore List: {ignore_list}")
#             print(f"Country List: {country_list}")

#             # Trigger the Celery task
#             print("Triggering Celery task...")
#             process_bot.delay(order.id, query, time_data, ignore_list, country_list)
#             print("Celery task triggered.")

#             return redirect('order_waiting', order_id=order.id)

#         return render(request, 'order_summary.html', {'order': order, 'order_details': order_details})

#     except Exception as e:
#         print(f"Error in order_summary view: {e}")
#         raise
# def order_summary(request, order_id):
#     print("Entering order_summary view...")
#     try:
#         order = Order.objects.get(id=order_id)
#         print(f"Order found: {order}")
#         order_details = OrderDetail.objects.filter(order=order)
#         print(f"Order details: {order_details}")
#         order_result = OrderResult.objects.filter(order_detail__order=order).first()
#         print(f"Order result: {order_result}")

#         if request.method == "POST":
#             print("POST request received.")
#             query = order_details.first().query  # Assuming all order details have the same query
#             ignore_list = MY_IGNORED_LIST
#             country_list = COUNTRY_LIST

#             print(f"Order ID: {order.id}")
#             print(f"Query: {query}")
#             print(f"Ignore List: {ignore_list}")
#             print(f"Country List: {country_list}")

#             # Trigger the Celery task with just the time_range
#             print("Triggering Celery task...")
#             process_bot.delay(order.id, query, order.time_range, ignore_list, country_list)  # Pass only time_range
#             print("Celery task triggered.")

#             return redirect('order_waiting', order_id=order.id)

#         return render(request, 'order_summary.html', {'order': order, 'order_details': order_details})

#     except Exception as e:
#         print(f"Error in order_summary view: {e}")
#         raise
