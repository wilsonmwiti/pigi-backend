from audioop import add
from django.shortcuts import render

from authentication.models import MyUser
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics,viewsets,permissions,status
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from authentication.serializer import UserSerializer
import json
from django.urls import reverse
from django_daraja.mpesa.core import MpesaClient
from django.core.cache import cache
import requests, os
from django.conf import settings
from requests.auth import HTTPBasicAuth
# Create your views here.

def generate_token():

	consumer_key = settings.VARIABLES.get('MPESA_CONSUMER_KEY')
	consumer_secret = settings.VARIABLES.get('MPESA_CONSUMER_SECRET')
	

	r = requests.get(settings.VARIABLES.get('TOKEN_URL'), auth=HTTPBasicAuth(consumer_key, consumer_secret))
	
	token=r.json()
	access_token = token.get('access_token')
	cache.set('access_token',access_token,1700)
	return token.get('access_token')

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def home_page(request):
  '''Retrieve logged in user details'''
  try:
    user = MyUser.objects.get(pk = request.user.id)
    print(user)
  except MyUser.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)
  if request.method == 'GET':
    serializer = UserSerializer(user)
    print(serializer.data)
    return Response(serializer.data)

@api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
def stk_push(request):
  data = request.data
  cl = MpesaClient()
  # callback_url = request.build_absolute_uri(reverse('mpesa_stk_push_callback'))
  response = cl.stk_push(data["phone_number"], data["amount"], data["account_ref"], data["description"], "https://0430-197-237-171-101.ngrok.io/payments/mpesa_stk_push_callback/")
  print(response.content)
  return HttpResponse(response)

@api_view(["GET"])
# @permission_classes([AllowAny])
def mpesa_stk_push_callback(request):

  data = request.body
  # # import pdb; pdb.set_trace()
  print(data)
  return HttpResponse({"message": "done"})

