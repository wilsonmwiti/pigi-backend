from django.urls import path
from . import views
from django.urls import re_path
urlpatterns = [
  path('goals/', views.GoalList.as_view()),
  path('new-goal/', views.GoalList.as_view()),
  path('get_goal/<uuid:url>/',views.GoalDescription.as_view())
  
]