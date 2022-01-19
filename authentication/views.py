from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import MyUser
from .serializer import RegisterSerializer, UserSerializer
from rest_framework import generics,viewsets,permissions
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

# Create your views here.
api_key = config("MSG_API_KEY")
sms_api_url = config("SMS_ENDPOINT")

def index(request):
  return HttpResponse('Pigibanks authentication default route')


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
def Register_Users(request):
    try:
        data = {}
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = True
            user.save()
            token = Token.objects.get_or_create(user=user)[0].key
            data["message"] = "user registered successfully"
            data["phone_number"] = user.phone_number
            data["first_name"] = user.first_name
            data["last_name"] = user.last_name
            data["token"] = token

        else:
            data = serializer.errors


        return Response(data)
    except IntegrityError as e:
        account=MyUser.objects.get(phone_number='')
        account.delete()
        raise ValidationError({"400": f'{str(e)}'})

    except KeyError as e:
        print(e)
        raise ValidationError({"400": f'Field {str(e)} missing'})

@api_view(["POST"])
@permission_classes([AllowAny])
def send_sms_code(request):
    """Function that send OTP message to client"""
    data ={}
    request_body = json.loads(request.body)
    print(request_body)
    phone_number = request_body['phone_number']
    print(phone_number)
    key = pyotp.random_base32()
    time_otp = pyotp.TOTP(key, interval=300, digits=4)
    time_otp = time_otp.now()
    message = "Your OTP is " + time_otp
    print(message)
    request.session.phone_number=time_otp
    payload = dict(sender='Sasa SMS',sms=message,msisdn=phone_number)
    
    r=requests.post(url=sms_api_url,json=payload,timeout=5, headers={"X-TOKEN":api_key})
    data["message"] = "Message has been sent successfully"
    data["phone_number"] = phone_number
    data['otp']=r
    response = {"data": data}

    return Response(response)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    data = {}
    
    otp_input = json.loads(request.body)
    otp=request.session[otp_input['phone_number']]
    
    otp_no = otp_input['otp_pin']
    if otp != otp_no:
        data["message"] = "Wrong PIN"
        response = {"data":data}
        return Response(response)
    else:
        data["message"] = "Phone number has been verified successfully"
        response = {"data":data}
        return Response(response)
        
    


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    data ={}
    reqBody = json.loads(request.body)
    print(reqBody)
    phone_number = reqBody['phone_number']
    password = '0000{}'.format(reqBody['password'])
    print(password)
    try:
        user = MyUser.objects.get(phone_number = phone_number)
    except BaseException as e:
        raise ValidationError({"400": f'{str(e)}'})
    token = Token.objects.get_or_create(user=user)[0].key
    print(token)
    if not check_password(password, user.password):
        raise ValidationError({"message": "Incorrect login credentials"})
    if user:
        if user.is_active:
            login(request, user)
            data["message"] = "user logged in"
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


