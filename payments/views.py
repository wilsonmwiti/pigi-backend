from audioop import add
from django.shortcuts import render

from authentication.models import MyUser
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics,viewsets,permissions,status
from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from authentication.serializer import UserSerializer
import json
from django.urls import reverse
from django_daraja.mpesa.core import MpesaClient
from django.core.cache import cache
import requests, os
from django.conf import settings
from requests.auth import HTTPBasicAuth
from savings.models import GeneralWallet,Goal
from decouple import config
from payments.models import Transactions
from savings.serializers import GeneralWalletSerializer, GoalSerializer
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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def add_funds(request):
  try:
    user = MyUser.objects.get(pk = request.user.id)
  except MyUser.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)
  if request.method == 'GET':
    general_wallet = GeneralWallet.objects.get(user = user)
    all_accounts = MyUser.objects.all(main_user_id = user)
    all_goals = Goal.objects.get(user = user)

    general_serializer = GeneralWalletSerializer(general_wallet, many=True)
    accounts_serializer = UserSerializer(all_accounts)
    goals_serializer = GoalSerializer(all_goals)
    dropdown_data = [
      {
        "type" : "general_wallet",
        "data" : general_serializer.data
      },
      {
        "type" : "Account",
        "data" : accounts_serializer.data
      },
      {
        "type" : "Goal",
        "data" : goals_serializer.data
      }
      ]
    return Response(dropdown_data)

    #Serialize all the querry_set data
    

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def stk_push(request):
  try:
    user = MyUser.objects.get(pk = request.user.id)
    print(user)
  except MyUser.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)
    
  data = request.data
  transaction_detail = data["description"]

  account_reference = config("MPESA_INITIATOR_USERNAME")
  cl = MpesaClient()
  # cl.access_token()
  # callback_url = request.build_absolute_uri(reverse('mpesa_stk_push_callback'))
  response = cl.stk_push(data["phone_number"], data["amount"],account_reference , data["description"],"https://a71a-197-237-171-101.ngrok.io/payments/mpesa_stk_push_callback/")
  
  callback_response = json.loads(response.content.decode('utf-8'))

  #Get the item that we are saving for

  transaction_id = callback_response.get('MerchantRequestID')
  # formated_data = transaction_detail.split()
  # item_type = formated_data[0]
  # item_id = int(formated_data[1])
  transaction_amount = data["amount"]
  Transactions.objects.create(user = user, transaction_id = transaction_id, type = 'D', 
  transaction_amount = transaction_amount, description = transaction_detail)
  return HttpResponse(response)

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def mpesa_stk_push_callback(request):
  data = json.loads(request.body.decode('utf-8'))
  
  # payload = json.loads(request)
  # data = {}
  callback = data['Body']['stkCallback']
  result_code =  data['ResultCode']
  print("RESULT CODE",result_code)
  metadata = callback.get('CallbackMetadata')
  metadata_items = metadata.get('Item')
  # if metadata:
  receipt_number = ''
  

  for item in metadata_items:
    if(item['Name'])=='MpesaReceiptNumber':
      receipt_number=item['Value']
      break
  print(receipt_number)
  
  	# data[item['Name']] = item.get('Value')
  # if callback['ResultCode'] == 0:
  #   try:
  #     transaction = Transactions.objects.filter(transaction_id= callback['MerchantRequestID']).update(
  #       status = 0
  #     )

  
  # result_code = cl.parse_stk_result(request)
  # print(result_code)
  
  # formatDict=dict(data)
  return JsonResponse(['Body']['stkCallback']['CallbackMetadata']['Item'])

