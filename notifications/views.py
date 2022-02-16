from django.shortcuts import render
import requests
from .models import Notification
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
# Create your views here.

@api_view(["GET","POST"])
@permission_classes([IsAuthenticated])
def create_notification(request):
  user = request.user
  if request.method == 'GET':
    notification = Notification.objects.get(user = request.user.id )
    
  pass