# dashboard/urls.py
from django.urls import path
from mydash import views  # Import your views module

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('choose-step/', views.choose_step, name='choose-step'),
    path('choose-manually/', views.choose_manually, name='choose_manually'),
    path('choose-by-filter/', views.choose_by_filter, name='choose_by_filter'),
    path('choose_keyword_time/<int:order_id>/', views.choose_keyword_time, name='choose_keyword_time'),
    path('order-summary/<int:order_id>/', views.order_summary, name='order_summary'),
    path('remove_order_detail/<int:order_detail_id>/', views.remove_order_detail, name='remove_order_detail'),
    path('order_waiting/<int:order_id>/', views.order_waiting, name='order_waiting'),
    #result of users search
    path('show_result/<int:order_id>/', views.show_result, name='show_result'),

    path('edit_order_detail/<int:detail_id>/', views.edit_order_detail, name='edit_order_detail'),

]

