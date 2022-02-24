from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_page),
    path('drop_down_items/', views.get_items_dropdown),
    path('stk_push/', views.stk_push, name='stk_push'),
    path('deposit/', views.deposit, name='deposit'),
    path('allocate/', views.allocate, name='allocate'),
    path('getTransactions', views.getTransactions, name='getTransactions'),
    path('mpesa_stk_push_callback/', views.mpesa_stk_push_callback,
         name='mpesa_stk_push_callback')

]
