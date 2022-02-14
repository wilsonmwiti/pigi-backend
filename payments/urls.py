from django.urls import path
from . import views



urlpatterns = [
  path('', views.home_page),
  path('stk_push/', views.stk_push, name='stk_push'),
  path('mpesa_stk_push_callback/', views.mpesa_stk_push_callback, name='mpesa_stk_push_callback')
  
]