from celery import shared_task
from mydash.bot.andishkadeh_bot import andishkadeh_bot
from .models import Order, OrderDetail, Status, OrderResult
import time

@shared_task(time_limit=600)
def process_bot(order_id, query, time_range, start_date, end_date, ignore_list, country_list):
    print("*****************Starting process_bot task... now I'm in tasks.py in the bot_process function************************")
    print(f"❌fromtasks❌Processing bot for Order ID: {order_id}")
    print(f"❌fromtasks❌Query: {query}")
    print(f"❌fromtasks❌Time Range: {time_range}, Start Date: {start_date}, End Date: {end_date}")

    # Initialize variables
    if time_range:
        print(f"Using predefined time range: {time_range}")
    else:
        print(f"Using custom date range: {start_date} to {end_date}")

    # Send the query to the bot and get the result
    print("❌ sending query to bot...")

    bot_result = andishkadeh_bot.perform_search_and_save_links(
        query,
        time_option=time_range,  # time_range for predefined time
        start_date=start_date,   # start_date for custom range
        end_date=end_date,       # end_date for custom range
        ignore_list=ignore_list,
        country_list=country_list,
        order_id=order_id
    )
    
    if not bot_result:
        raise ValueError("❌ Bot did not return a valid result")

    # Save the result in the OrderResult model
    order = Order.objects.get(id=order_id)
    order_details = OrderDetail.objects.filter(order=order)

    # Store the result file (Excel file, etc.)
    result_file = bot_result  # Assuming bot returns a file path or a file

    for order_detail in order_details:
        order_result = OrderResult.objects.create(
            order_detail=order_detail,
            status=Status.objects.get(name="Completed"),
            result_file=result_file  # Save the result file (file path or actual file)
        )
        # Update the `is_processed` flag when the result is created
        order_result.is_processed = True
        order_result.save()
    # Optionally, update the order's status
    order.final_status = Status.objects.get(name="Completed")
    order.save()

    print(f"Order status updated to 'Completed' for Order ID: {order_id}")


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def add(self, x, y):
    try:
        print('❌❌❌❌❌❌❌❌❌❌❌my simple sample❌❌❌❌❌❌❌❌❌❌❌❌❌')
        return x + y
    except Exception as e:
        print(f"Task failed due to: {str(e)}")
        raise self.retry(exc=e)