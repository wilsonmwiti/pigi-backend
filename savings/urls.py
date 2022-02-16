from django.urls import path
from . import views
from django.urls import re_path
urlpatterns = [
  path('goals/', views.GoalList.as_view()),
  path('new-goal/', views.GoalList.as_view()),
  path('get_goal/<uuid:url>/',views.GoalDescription.as_view()),
  path('new-locked-svgs/', views.LockedSavingsList.as_view()),
  path('get_savings/<uuid:url>/',views.LockedSavingsDesc.as_view())
  
  
]