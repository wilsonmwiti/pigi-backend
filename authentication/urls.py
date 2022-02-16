from unicodedata import name
from django.urls import path
from . import views



urlpatterns = [
  path('', views.index, name = 'index'),
  path('register/', views.Register_Users ),
  path('add_account/', views.add_account),
  path('get_user/', views.get_user),
  path('get_profile/', views.get_profile),
  path('login/', views.login_user ),
  path('logout/', views.User_logout ),
  path('users/', views.users_list),
  path('OTP-sms/', views.send_sms_code),
  path('forgot-pass/', views.edit_password),
  path('load_nav/', views.load_side_nav)
 
]
