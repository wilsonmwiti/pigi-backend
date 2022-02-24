import datetime
from django.http import JsonResponse
from django.shortcuts import render
import requests
from authentication.models import MyUser

from notifications.serializer import NotificationSerializer
from .models import Notification
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from decouple import config
# Create your views here.

api_key = config("MSG_API_KEY")
sms_api_url = config("SMS_ENDPOINT")


def create_notification(data):
    notification = Notification(
        user=data['user'],
        isPositive=data['isPositive'],
        message=data['message'],
    )
    if 'action' in data:
        notification.action = data['action']

    notification.save()
    sendSMS(data['phone_number'], data['message'])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getNotifications(request):
    try:
        notifications = Notification.objects.filter(
            user=request.user.id).order_by("-created_date")

        serializer = NotificationSerializer(notifications, many=True)

        response = {
            "status": 1,
            "data": serializer.data
        }
        for i in serializer.data:
            user = MyUser.objects.filter(id=request.user.id).values(
                'first_name', "thumbnail").first()
            i['user'] = {
                "name": user['first_name'],
                "thumbnail": user['thumbnail']
            }

        return JsonResponse(response)

    except Exception as e:
        response = {
            "status": 0,
            "data": {
                "message": "Error occured. {}".format(e)}
        }
        return JsonResponse(response)


def depositedNotificationMessage(amount, target):
    return "Congratulations. You have deposited {} towards {}".format(amount, target)


def allocateNotificationMessage(amount, target):
    return "Congratulations. You have allocated {} towards {}".format(amount, target)


def reminderNotificationMessage(amount, target):
    return "You are reminded to save {} towards {}".format(amount, target)


def sendSMS(phone_number, message):
    headers = {
        "Accept": '*/*',
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        'Content-Type': 'application/json',
        "X-TOKEN": api_key
    }
    myobject = {
        "msisdn": phone_number,
        "sms": message,
        "sender": "PIGI"

    }
    # data to be sent to the api

    r = requests.post(sms_api_url, json=myobject, timeout=5, headers=headers)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getNotificationStatus(request):
    unread = True
    try:
        notifications = Notification.objects.filter(
            user=request.user.id, is_read=False)

        if len(notifications) > 0:
            unread = True
        else:
            unread = False

        response = {
            "status": 1,
            "data": {
                "unread": unread
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
def updateNotificationStatus(request):
    try:
        notifications = Notification.objects.filter(
            user=request.user.id, is_read=False).update(is_read=True)

        response = {
            "status": 1,
            "data": {
                "message": "Notifactions updated successfuly"
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filterNotifications(request):
    try:
        start = datetime.datetime.strptime(request.data['start'], '%Y-%m-%d')
        end = datetime.datetime.strptime(request.data['end'], '%Y-%m-%d')
        notifications = Notification.objects.filter(
            user=request.user.id, date_added__range=(start, end))
        serializer = NotificationSerializer(notifications, many=True)

        response = {
            "status": 1,
            "data": serializer.data
        }

        for i in serializer.data:
            user = MyUser.objects.filter(id=request.user.id).values(
                'first_name', "thumbnail").first()
            i['user'] = {
                "name": user['first_name'],
                "thumbnail": user['thumbnail']
            }

        return JsonResponse(response)
    except Exception as e:
        response = {
            "status": 0,
            "data": {
                "message": "Error occured. {}".format(e)}
        }
        return JsonResponse(response)
