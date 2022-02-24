from django.urls import path
from . import views

urlpatterns = [
    path('', views.getNotifications, name='notifications'),
    path('getNotificationStatus/', views.getNotificationStatus,
         name='getNotificationStatus'),
    path('updateNotificationStatus', views.updateNotificationStatus,
         name='updateNotificationStatus'),
    path('filterNotifications', views.filterNotifications,
         name='filterNotifications'),
]
