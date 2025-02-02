from celery import shared_task
from mydash.bot.andishkadeh_bot import andishkadeh_bot

from .models import Order, OrderDetail, Status, OrderResult
import time



# @shared_task(time_limit=300)
# def process_bot(order_id, query, time_data, ignore_list, country_list):
#     print("Starting process_bot task...")

#     print(f"Processing bot for Order ID: {order_id}")
#     print(f"Query: {query}")
#     print(f"Time Data: {time_data}")
#     print(f"Ignore List: {ignore_list}")
#     print(f"Country List: {country_list}")
#     # Check if time_data is valid
#     if isinstance(time_data, dict):  # Custom date range
#         start_date = time_data.get('start_date')
#         end_date = time_data.get('end_date')
#     elif isinstance(time_data, str):  # Predefined time range
#         time_range = time_data
#     else:
#         # If invalid time_data is provided, handle gracefully (raise error or use a default)
#         raise ValueError("Invalid time_data provided")
    
    
    
#     print("Sending query to bot...")

#     # Send the query to the bot and get the result
#     bot_result = andishkadeh_bot.perform_search_and_save_links(query, time_option=time_range, 
#                                                                start_date=start_date, end_date=end_date,
#                                                                ignore_list=ignore_list, country_list=country_list,
#                                                                order_id=order.id)
    
#     if not bot_result:
#         raise ValueError("Bot did not return a valid result")

#     # Save the result in the OrderResult model
#     order = Order.objects.get(id=order_id)
#     order_details = OrderDetail.objects.filter(order=order)

#     # Store the result file (Excel file, etc.)
#     result_file = bot_result  # Assuming bot returns a file path or a file

#     for order_detail in order_details:
#         OrderResult.objects.create(
#             order_detail=order_detail,
#             status=Status.objects.get(name="Completed"),
#             result_file=result_file  # Save the result file (file path or actual file)
#         )

#     # Optionally, update the order's status
#     order.final_status = Status.objects.get(name="Completed")
#     order.save()

#     # Check if time_data is valid
#     if isinstance(time_data, dict):  # Custom date range
#         start_date = time_data.get('start_date')
#         end_date = time_data.get('end_date')
#         print(f"Using custom date range: {start_date} to {end_date}")

#     elif isinstance(time_data, str):  # Predefined time range
#         time_range = time_data
#         print(f"Using predefined time range: {time_range}")

#     else:
#         # If invalid time_data is provided, handle gracefully (raise error or use a default)
#         print("Invalid time_data provided, raising an exception")
#         raise ValueError("Invalid time_data provided")
    
#     print("Sending query to bot...")
#     # Send the query to the bot and get the result
#     bot_result = andishkadeh_bot.perform_search_and_save_links(query)
    
#     if not bot_result:
#         print("Bot did not return a valid result.")
#         raise ValueError("Bot did not return a valid result")

#     # Save the result in the OrderResult model
#     order = Order.objects.get(id=order_id)
#     order_details = OrderDetail.objects.get(order=order)
#     print(f"Saving result to OrderResult for Order ID: {order_id}")

#     # Store the result file (Excel file, etc.)
#     result_file = bot_result  # Assuming bot returns a file path or a file

#     for order_detail in order_details:
#         OrderResult.objects.create(
#             order_detail=order_detail,
#             status=Status.objects.get(name="Completed"),
#             result_file=result_file  # Save the result file (file path or actual file)
#         )

#     # Optionally, update the order's status
#     order.final_status = Status.objects.get(name="Completed")
#     order.save()
#     print(f"Order status updated to 'Completed' for Order ID: {order_id}")

@shared_task(time_limit=600)
def process_bot(order_id, query, time_data, ignore_list, country_list):
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&start bot &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    print("Starting process_bot task...")

    print(f"Processing bot for Order ID: {order_id}")
    print(f"Query: {query}")
    print(f"Time Data: {time_data}")
    print(f"Ignore List: {ignore_list}")
    print(f"Country List: {country_list}")

    # Initialize the variables
    start_date = None
    end_date = None
    time_range = None

    # Check if time_data is a dictionary (custom date range)
    if isinstance(time_data, dict):  
        start_date = time_data.get('start_date')
        end_date = time_data.get('end_date')
    elif isinstance(time_data, str):  # If time_data is a string (predefined time range or 'Any time')
        if time_data == 'Any time':
            print("Using 'Any time' as the time option. No date range.")
        else:
            time_range = time_data  # Assign the predefined time range
    else:
        raise ValueError("Invalid time_data provided")

    # Send the query to the bot and get the result
    print("Sending query to bot...")

    bot_result = andishkadeh_bot.perform_search_and_save_links(query, time_option=time_range, 
                                                               start_date=start_date, end_date=end_date,
                                                               ignore_list=ignore_list, country_list=country_list,
                                                               order_id=order_id)
    
    if not bot_result:
        raise ValueError("Bot did not return a valid result")

    # Save the result in the OrderResult model
    order = Order.objects.get(id=order_id)
    order_details = OrderDetail.objects.filter(order=order)

    # Store the result file (Excel file, etc.)
    result_file = bot_result  # Assuming bot returns a file path or a file

    for order_detail in order_details:
        OrderResult.objects.create(
            order_detail=order_detail,
            status=Status.objects.get(name="Completed"),
            result_file=result_file  # Save the result file (file path or actual file)
        )

    # Optionally, update the order's status
    order.final_status = Status.objects.get(name="Completed")
    order.save()

    print(f"Order status updated to 'Completed' for Order ID: {order_id}")

@shared_task
def simple_task():
    print("**********Task started!")
    time.sleep(5)  # Simulate some work
    print("##########Task completed!")
    
@shared_task
def another_simple_task():
    print("Task is running")
    return "Task complete"