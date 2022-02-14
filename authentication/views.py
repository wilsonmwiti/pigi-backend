from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import MyUser
from .serializer import RegisterSerializer, RegisterSubaccountSerializer, UserSerializer
from rest_framework import generics,viewsets,permissions,status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login,logout
import json
import pyotp
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import requests
import uuid

from authentication import serializer

# Create your views here.
api_key = config("MSG_API_KEY")
sms_api_url = config("SMS_ENDPOINT")

def index(request):
  return HttpResponse('Pigibanks authenticattion default route api')


@csrf_exempt
def users_list(request):
    """
    List all users
    """
    if request.method == 'GET':
        queryset = MyUser.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(["POST"])
@permission_classes([AllowAny])
def get_user(request):
    '''Verify a phone number exists'''
    data = {}
    request_body = json.loads(request.body)
    phone_number = request_body['phone_number']
    try:
        user = MyUser.objects.get(phone_number = phone_number)
    except MyUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data["first_name"] = user.first_name
    data["phone_number"] = user.phone_number

    return Response(data)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_account(request):
    '''Adding a sub-account'''
    try:
        data = {}
        serializer = RegisterSubaccountSerializer(data=request.data)
        if serializer.is_valid():
            # user_id = uuid.uuid4
            user = serializer.save(main_user_id = request.user.id)
            # token = Token.objects.get_or_create(user=user)[0].key
            data['message'] = "Account has been added successfully"
            data['first_name'] = user.first_name
            data["last_name"] = user.last_name
            data["username"] = user.username
            data["main_account_id"] =request.user.id
            # data["token"] = token
        else:
            data = serializer.errors
        return Response(data)
    except KeyError as e:
        print(e)
        raise ValidationError({"400": f'Field {str(e)} missing'})

@api_view(["POST"])
@permission_classes([AllowAny])
def Register_Users(request):
    try:
        data = {}
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # user_id = uuid.uuid4
            user = serializer.save()
            # print(user)
            token = Token.objects.get_or_create(user=user)[0].key
            data["message"] = "user registered successfully"
            data["phone_number"] = user.phone_number
            data["first_name"] = user.first_name
            data["last_name"] = user.last_name
            data["token"] = token

        else:
            data = serializer.errors


        return Response(data)
    # except IntegrityError as e:
    #     account=MyUser.objects.get(phone_number='')
    #     account.delete()
    #     raise ValidationError({"400": f'{str(e)}'})

    except KeyError as e:
        print(e)
        raise ValidationError({"400": f'Field {str(e)} missing'})

@api_view(["POST",])
@permission_classes([AllowAny])
def send_sms_code(request):
    """Function that send OTP message to client"""
    data ={}
    request_body = json.loads(request.body)
    phone_number = request_body['phone_number']
    key = pyotp.random_base32()
    time_otp = pyotp.TOTP(key, interval=300, digits=4)
    time_otp = time_otp.now()
    message = "Your OTP is " + time_otp
    # payload = dict(sender='Sasa SMS',sms=message,msisdn=phone_number)
    myobject = {
        "msisdn": phone_number,
        "sms" : message,
        "sender" : "PIGI"

    }
    headers = {
        "Accept": '*/*',
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        'Content-Type': 'application/json',
        "X-TOKEN":api_key
    }
    #data to be sent to the api 
   
    r=requests.post(sms_api_url,json=myobject,timeout=60, headers=headers)

    response = r.text
    data["message"] = "Message has been sent successfully"
    data["phone_number"] = phone_number
    data['otp']=time_otp
    response = {"data": data}
    return Response(response)

@api_view(["PUT",])
@permission_classes([AllowAny])
def edit_password(request):
    '''Edit users password'''
    data ={}
    reqBody = json.loads(request.body)
    phone_number = reqBody['phone_number']
    password = reqBody['password']
    try:
        user = MyUser.objects.get(phone_number = phone_number)
    except MyUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        user.set_password(password)
        user.save()
        serializer =UserSerializer(user)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


 


@api_view(["GET","PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    '''Retrieve user profile details'''
    try:
        user = MyUser.objects.get(pk = request.user.id)
        print(user)
    except MyUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        print(serializer.data)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save(visibility = 0)
        print(user.visibility)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    data ={}

    reqBody = json.loads(request.body)
    phone_number = reqBody['phone_number']
    password =reqBody['password']

    try:
        user = MyUser.objects.get(phone_number = phone_number)
    except BaseException as e:
        raise ValidationError({"400": f'{str(e)}'})
    token = Token.objects.get_or_create(user=user)[0].key
    if not check_password(password, user.password):
        raise ValidationError({"message": "Incorrect login credentials"})
    if user:
        if user.is_active:
            login(request, user)
            data["message"] = "user createlogged in"
            data["phone_number"] = user.phone_number
            Res = {"data": data, "token": token}

            return Response(Res)
        else:
            raise ValidationError({"400": f'Account not active'})
    else:
        raise ValidationError({"400": f'Account doesn\'t exist'})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def User_logout(request):
    request.user.auth_token.delete()
    logout(request)
    return Response('User logged out successfully')


