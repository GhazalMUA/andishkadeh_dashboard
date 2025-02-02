from django.shortcuts import render, redirect
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
            keyword="Filtered Selection",
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
    """after selecting the research center its the time to select keyword and time
    Args:
        request (user can set the time in some ): _description_
        order_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        keyword = request.POST.get('keyword')  # Get the keyword from user input
        selected_time_range = request.POST.get('time_range')  # Get the selected time range
        start_date = request.POST.get('start_date')  # Custom start date
        end_date = request.POST.get('end_date')  # Custom end date
        
        # a ge hardotaro entekhab kard.
        if selected_time_range and (start_date or end_date):
            return render(request, 'choose_keyword_time.html', {'error': "Please select either a time range or custom date range, not both."})
        if selected_time_range:
            order.time_range = selected_time_range
        elif start_date and end_date:
            order.start_date = datetime.strptime(start_date, '%Y-%m-%d')
            order.end_date = datetime.strptime(end_date, '%Y-%m-%d')  
            order.save()  
        order_detail = OrderDetail.objects.get(order=order)
        research_center = order_detail.research_center
        query = generate_query(keyword=keyword, website=research_center.website)
        order_detail.query = query
        time_data = None
        if selected_time_range:
            time_data = selected_time_range
        elif start_date and end_date:
            time_data = {'start_date': start_date, 'end_date': end_date}
            
        if selected_time_range and (start_date or end_date):
            return render(request, 'choose_keyword_time.html', {'error': "Please select either a time range or custom date range, not both."})

        if start_date and not end_date:
            return render(request, 'choose_keyword_time.html', {'error': "Both start and end dates are required for a custom range."})

        if end_date and not start_date:
            return render(request, 'choose_keyword_time.html', {'error': "Both start and end dates are required for a custom range."})
            
        order_detail.save()
        
        return redirect( 'order_summary', order_id=order_id)
    
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
            time_data = {
                'start_date': order.start_date,
                'end_date': order.end_date,
                'time_range': order.time_range
            }
            ignore_list = MY_IGNORED_LIST
            country_list = COUNTRY_LIST

            print(f"Order ID: {order.id}")
            print(f"Query: {query}")
            print(f"Time Data: {time_data}")
            print(f"Ignore List: {ignore_list}")
            print(f"Country List: {country_list}")

            # Trigger the Celery task
            print("Triggering Celery task...")
            process_bot.delay(order.id, query, time_data, ignore_list, country_list)
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
    




