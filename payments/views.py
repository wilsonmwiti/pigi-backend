from ast import Global
from audioop import add
import datetime
import base64
from wsgiref.util import request_uri
from django.shortcuts import render

from authentication.models import MyUser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from authentication.serializer import UserSerializer
import json
from django.db.models import F
from django.urls import reverse
from django_daraja.mpesa.core import MpesaClient, format_phone_number
from django.core.cache import cache
import requests
import os
from django.conf import settings
from requests.auth import HTTPBasicAuth
from payments.serializer import TransactionSerializer
from savings.models import GeneralWallet, Goal, LockedSavings
from decouple import config
from payments.models import Transactions
from savings.serializers import GeneralWalletSerializer, GoalSerializer
from notifications.views import depositedNotificationMessage, create_notification, sendSMS, allocateNotificationMessage, reminderNotificationMessage
# Create your views here.


def generateKeys():
    try:
        response=requests.get(
                    "{}/oauth/v1/generate?grant_type=client_credentials".format(config("MPESA_DOMAIN")), 
                    auth=HTTPBasicAuth(config("MPESA_CONSUMER_KEY"), config("MPESA_CONSUMER_SECRET"))
                    )
        formattedResponse=dict(json.loads(response.text))
        print(formattedResponse)
        return formattedResponse['access_token']
    except Exception as e:
        print(e)
        return HttpResponse(e)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def home_page(request):
    '''Retrieve logged in home page user details'''
    try:
        accountBalance = MyUser.objects.get(pk=request.user.id).account_balance
        generalWalletBalance = GeneralWallet.objects.get(
            user=request.user.id).amount

        response = {
            "status": 1,
            "data": {
                "account_balance": accountBalance,
                "general_wallet": generalWalletBalance
            }
        }
        return JsonResponse(response)

    except Exception as e:
        response = {
            "status": 0,
            "data": {
                "message": "Error occured. {}".format(e)}
        }
        return JsonResponse(response)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_items_dropdown(request):
    try:
        user = MyUser.objects.get(pk=request.user.id)
        if request.method == 'GET':
            general_wallet = GeneralWallet.objects.filter(
                user=user.id).values('id', 'amount')
            all_accounts = MyUser.objects.filter(
                main_user_id=user.id).values('id', 'first_name', 'last_name')
            all_goals = Goal.objects.filter(
                user=user.id).values('id', "goal_name")
            locked_savings = LockedSavings.objects.filter(
                user=user.id).values('id', "item_name")

            dropdown_data = [
                {
                    "type": "general_wallet",
                    "data": general_wallet
                },
                {
                    "type": "Account",
                    "data": all_accounts
                },
                {
                    "type": "Goal",
                    "data": all_goals
                },
                {
                    "type": "Locked savings",
                    "data": locked_savings
                },
            ]
            response = {
                "status": 1,
                "data": dropdown_data
            }
            return Response(response)
    except Exception as e:
        response = {
            "status": 0,
            "data": {
                "message": "Error occured. {}".format(e)}
        }
        return JsonResponse(response)

        # Serialize all the querry_set data


def stk_push(data):
    transaction_detail = data["description"]
    transaction_amount = data["amount"]
    user = data['user']
    print(data)
    phone_number = format_phone_number(data['phone_number'])
    url = '{}/mpesa/stkpush/v1/processrequest'.format(config("MPESA_DOMAIN"))
    passkey = config('MPESA_PASSKEY')
    
    mpesa_environment = config('MPESA_ENVIRONMENT')
    if mpesa_environment == 'sandbox':
        business_short_code = config('MPESA_EXPRESS_SHORTCODE')
    else:
        business_short_code = config('MPESA_SHORTCODE')

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((business_short_code + passkey + timestamp).encode('ascii')).decode('utf-8') 
    transaction_type = 'CustomerPayBillOnline'
    party_a = phone_number
    party_b = business_short_code

    data = {
        'BusinessShortCode': business_short_code,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': transaction_type,
        'Amount': transaction_amount,
        'PartyA': party_a,
        'PartyB': party_b,
        'PhoneNumber': phone_number,
        'CallBackURL': "https://pigibank-bcknd.herokuapp.com/payments/mpesa_stk_push_callback/",
        'AccountReference': "PIGIBANK",
        'TransactionDesc': transaction_detail
    }

    headers = {
        'Authorization': 'Bearer ' + generateKeys(),
        'Content-type': 'application/json'
    }
    r = requests.post(url, json=data, headers=headers)
    response = dict(json.loads(r.text))



    # Get the item that we are saving for

    transaction_id = response.get('MerchantRequestID')
    print(transaction_id)
    
    Transactions.objects.create(user=user, transaction_id=transaction_id, type='D',
                                transaction_amount=transaction_amount, description=transaction_detail)
    return transaction_id


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def allocate(request):
    try:
        splitItem = request.data['item'].split()
        # responseData=stk_push(request.data)
        amount = request.data['amount']

        generalWalletBalance = GeneralWallet.objects.get(
            user=request.user.id).amount

        if(int(amount) > generalWalletBalance):
            raise Exception("Insufficient funds at the general wallet")
        else:
            if (splitItem[0] == "goal"):
                goal_id = splitItem[1]
                goalName = Goal.objects.get(id=goal_id).goal_name
                goal = Goal.objects.filter(id=goal_id).update(
                    current_saving=F('current_saving') + amount)

            elif (splitItem[0] == "account"):
                goal_id = splitItem[1]
                goalName = MyUser.objects.get(id=goal_id).first_name
                goal = MyUser.objects.filter(id=goal_id).update(
                    acount_balance=F('acount_balance') + amount)
            elif (splitItem[0] == "locked_savings"):
                goal_id = splitItem[1]
                goalName = LockedSavings.objects.get(id=goal_id).item_name
                goal = LockedSavings.objects.filter(id=goal_id).update(
                    current_saving=F('current_saving') + amount)

                # deduct from general wallet
            goal = GeneralWallet.objects.filter(
                user=request.user.id).update(amount=F('amount') - amount)

            # add transaction
            Transactions.objects.create(user=request.user, transaction_id="null2", type='D',
                                        transaction_amount=amount, description=request.data['item'])

            # send notification
            notificationData = {
                "user": request.user,
                "isPositive": True,
                "message": allocateNotificationMessage(amount=amount, target="{} {}".format(splitItem[0], goalName)),
                "phone_number": request.user.phone_number
            }
            create_notification(notificationData)
            sendSMS(notificationData['phone_number'], depositedNotificationMessage(
                amount=amount, target="{} {}".format(splitItem[0], goalName)))

        response = {
            "status": 1,
            "data": {
                "message": "Amount allocated successfully"}
        }

        return JsonResponse(response)
    except Exception as e:
        response = {
            "status": 0,
            "data": {
                "message": "Error occured. {}".format(e)}
        }
        return JsonResponse(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deposit(request):
    try:
        data = {
            "description": request.data['item'],
            "user": request.user,
            "amount": int(request.data['amount']),
            "phone_number": request.user.phone_number,
        }
        print(request.data)
        responseData = stk_push(data)

        response = {
            "status": 1,
            "data": {
                "message": "Deposit currently undergoing",
                "desc": request.data['item']
            }
        }

        return JsonResponse(response)
    except Exception as e:
        response = {
            "status": 0,
            "data": {
                "message": "Error occured. {}".format(e)}
        }
        return JsonResponse(response)


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def mpesa_stk_push_callback(request):
    data = json.loads(request.body.decode('utf-8'))

    # payload = json.loads(request)
    # data = {}
    callback = data['Body']['stkCallback']
    result_code = callback['ResultCode']
    if result_code == 0:
        metadata = callback.get('CallbackMetadata')
        metadata_items = metadata.get('Item')
        # if metadata:
        receipt_number = ''

        for item in metadata_items:
            if(item['Name']) == 'MpesaReceiptNumber':
                receipt_number = item['Value']
                break

        try:
            transaction = Transactions.objects.filter(transaction_id=callback['MerchantRequestID']).update(
                status=0, mpesa_receipt_number=receipt_number)
        except Transactions.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        transaction = Transactions.objects.get(
            mpesa_receipt_number=receipt_number)
        description = transaction.description
        description_list = description.split()
        amount = transaction.transaction_amount
        user = transaction.user
        account = MyUser.objects.filter(id=user.id).update(
            account_balance=F('account_balance') + amount)
        if "goal" in transaction.description:
            goal_id = description_list[1]

            try:
                goal = Goal.objects.filter(id=goal_id).update(
                    current_saving=F('current_saving') + amount)
                targetGoal = Goal.objects.get(id=goal_id).goal_name
                message = depositedNotificationMessage(amount, targetGoal)
                notificationData = {
                    "user": user,
                    "isPositive": True,
                    "message": message,
                    "phone_number": user.phone_number
                }
                create_notification(notificationData)
                sendSMS(notificationData['phone_number'],
                        notificationData['message'])
            except Goal.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        elif "account" in transaction.description:
            account_id = description_list[1]
            try:
                sub_account = MyUser.objects.filter(id=user.id).update(
                    current_saving=F('account_balance') + amount)
                first_name = MyUser.objects.get(id=user.id).first_name
                message = depositedNotificationMessage(amount, first_name)
                notificationData = {
                    "user": user,
                    "isPositive": True,
                    "message": message,
                    "phone_number": user.phone_number
                }
                create_notification(notificationData)
                sendSMS(notificationData['phone_number'],
                        notificationData['message'])
            except MyUser.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        elif "locked_saving" in transaction.description:
            locked_saving_id = description_list[1]
            try:
                locked_saving = LockedSavings.objects.filter(
                    id=locked_saving_id).update(status=1, current_total=amount)
                item_name = LockedSavings.objects.get(
                    id=locked_saving_id).item_name
                message = depositedNotificationMessage(amount, item_name)
                notificationData = {
                    "user": user,
                    "isPositive": True,
                    "message": message,
                    "phone_number": user.phone_number
                }
                create_notification(notificationData)
                sendSMS(notificationData['phone_number'],
                        notificationData['message'])
            except LockedSavings.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            general_wallet = GeneralWallet.objects.filter(
                user=user).update(amount=F('amount') + amount)
            message = depositedNotificationMessage(
                amount, "your general wallet")
            notificationData = {
                "user": user,
                "isPositive": True,
                "message": message,
                "phone_number": user.phone_number
            }
            create_notification(notificationData)
            sendSMS(notificationData['phone_number'],
                    notificationData['message'])

    else:
        transaction = Transactions.objects.filter(
            transaction_id=callback['MerchantRequestID']).delete()
        return JsonResponse({"error": "{}".format("Transaction cancelled by user")})

    formatDict = dict(data)
    return JsonResponse(formatDict['Body']['stkCallback']['CallbackMetadata']['Item'], safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTransactions(request):
    try:
        start = datetime.datetime.strptime(request.data['start'], '%Y-%m-%d')
        end = datetime.datetime.strptime(request.data['end'], '%Y-%m-%d')
        transactions = Transactions.objects.filter(
            user=request.user.id, created_at__range=(start, end))
        serializer = TransactionSerializer(transactions, many=True)

        response = {
            "status": 1,
            "data": serializer.data
        }

        return JsonResponse(response)
    except Exception as e:
        response = {
            "status": 0,
            "data": {
                "message": "Error occured. {}".format(e)}
        }
        return JsonResponse(response)
