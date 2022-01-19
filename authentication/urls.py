from unicodedata import name
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
  path('', views.index, name = 'index'),
  path('register/', views.Register_Users ),
  path('login/', views.login_user ),
  path('logout/', views.User_logout ),
  path('users/', views.users_list),
  path('OTP-sms/', views.send_sms_code),
  path('verify_otp/', views.verify_otp)
]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)