import datetime
import uuid
from django.shortcuts import render
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
import json
from .models import Goal, LockedSavings
from .serializers import GoalSerializer, LockedSavingSerializer
from rest_framework.authentication import TokenAuthentication
from payments.views import stk_push
# Create your views here.

class  GoalList(APIView):
  permission_classes = [IsAuthenticated,]
  def get(self, request, format=None):
    try:
        all_goals = Goal.objects.filter(user = request.user)
        serializers = GoalSerializer(all_goals, many=True)

        response={
            "status":1,
            "data":serializers.data
        }
        return Response(response)
    except Exception as e:
        response={
            "status":0,
            "data":{
                "message":"Error occured. {}".format(e)}
        }
        return JsonResponse(response)

  def get_goal(self, uuid):
        try:
            return Goal.objects.get(goal_id=uuid)
        except Goal.DoesNotExist:
            return Http404


  def post(self, request, format=None):
    try:
        if(request.data['type'] == "new"):
            auto_save = bool(request.data['auto_save'])
            today = datetime.datetime.now()

            start_time = today.strftime("%H:%M:%S.%f")
            input_maturity_date = datetime.datetime.strptime(request.data['maturity_date'], '%Y-%m-%d %H:%M:%S.%f')
            maturity_date = input_maturity_date.strftime("%y-%m-%d")
            daily_amount = request.data['daily_amount']
        
            
            date_time_obj = maturity_date + " " + start_time

            final_maturity_date = datetime.datetime.strptime(date_time_obj, '%y-%m-%d %H:%M:%S.%f')

            goal = Goal(
                goal_name= request.data['goal_name'],
                target_amount =  request.data['target_amount'],
                maturity_date =  final_maturity_date,
                daily_amount = daily_amount,
                auto_save = auto_save,
                user=request.user,
                goal_id=uuid.uuid4()
            )
            if "thumbnail" in request.data:
                goal.thumbnail =request.data['thumbnail']

            goal.save()
            response={
                "status":1,
                "data":{
                    "message":"Goal saving created successfuly",
                }
            }
        else:
            goal = self.get_goal(request.data['goal_id'])
            serializer = GoalSerializer(goal, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response={
                "status":1,
                "data":{
                    "message":"Goal saving updated successfuly",
                    }
                }
                return Response(response)
            else:
                raise Exception(serializer.errors)
        return Response(response)
    except Exception as e:
        response={
            "status":0,
            "data":{
                "message":"Error occured. {}".format(e)}
        }
        return JsonResponse(response)

class GoalDescription(APIView):
    permission_classes = (IsAuthenticated,)
    def get_goal(self, uuid):
        try:
            return Goal.objects.get(goal_id=uuid)
        except Goal.DoesNotExist:
            return Http404
    def get(self, request, url, format=None):
        try:
            goal = self.get_goal(url)
            serializers = GoalSerializer(goal)

            response={
                "status":1,
                "data":serializers.data
            }
            return Response(response)
        except Exception as e:
            response={
                "status":0,
                "data":{
                    "message":"Error occured. {}".format(e)}
            }
            return JsonResponse(response)
    
    

    def delete(self, request, url, format=None):
        try:
            goal = self.get_goal(url)
            goal.delete()

            response={
                "status":1,
                "data":{
                    "message":"Goal saving deleted successfuly",
                    }
                }
            return Response(response)
        except Exception as e:
            response={
                "status":0,
                "data":{
                    "message":"Error occured. {}".format(e)}
            }
            return JsonResponse(response)

class  LockedSavingsList(APIView):
    '''An api that gets a list of all locked savings for a particular user'''
    permission_classes = [IsAuthenticated,]
    def get_savings(self, uuid):
        try:
            return LockedSavings.objects.get(savings_id=uuid)
        except LockedSavings.DoesNotExist:
            return Http404
    def get(self, request, format=None):
        try:
            all_locked = LockedSavings.objects.filter(user = request.user)
            serializers = LockedSavingSerializer(all_locked, many=True)
            for item in serializers.data:
                item['goal_id']=item.pop('savings_id')
                item['goal_name']=item.pop('item_name')
            response={
                "status":1,
                "data":serializers.data
            }
            return JsonResponse(response)
        except Exception as e:
            response={
                "status":0,
                "data":{
                    "message":"Error occured. {}".format(e)
                }
            }
            return JsonResponse(response)
        
        

    def post(self, request, format=None):
        try:
            if(request.data['type'] == "new"):
                print(request.data)
                serializers = LockedSavingSerializer(data=request.data)
                if serializers.is_valid():
                    savings_id = uuid.uuid4()
                    serializers.save(user = request.user , savings_id = savings_id)
                    data={
                        "description":"locked_saving {}".format(serializers.data['id']),
                        "user":request.user,
                        "amount":serializers.data['principal_deposit'],
                    }
                    # stk_push(data)

                    response = {
                        "status":1,
                        "data":{
                            "message":"Locked saving created successfuly",
                            "desc":data['description']
                        }
                    }
                    
                    return Response(response)

                raise Exception(serializers.errors)
            else:
                locked_savings = self.get_savings(request.data['goal_id'])
                serializer = LockedSavingSerializer(locked_savings, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    response={
                    "status":1,
                    "data":{
                        "message":"Goal saving updated successfuly",
                        }
                    }
                    return Response(response)
                else:
                    return Response(serializer.errors)
        except Exception as e:
            response={
                "status":0,
                "data":{
                    "message":"Error occured. {}".format(e)}
            }
            return JsonResponse(response)

class LockedSavingsDesc(APIView):
    permission_classes = (IsAuthenticated,)
    def get_savings(self, uuid):
        try:
            return LockedSavings.objects.get(savings_id=uuid)
        except LockedSavings.DoesNotExist:
            return Http404


    def get(self, request, url, format=None):
        try:
            locked_savings = self.get_savings(url)
            serializers = LockedSavingSerializer(locked_savings)
            
            response={
                "status":1,
                "data":serializers.data
            }
            response['data']['goal_id']=response['data'].pop("savings_id")
            response['data']['goal_name']=response['data'].pop("item_name")
            response['data']['target_amount']=response['data'].pop("principal_deposit")
            response['data']['current_saving']=response['data'].pop("current_total")
            response['data']['start_date']=response['data'].pop("date_added")
            return Response(response)
        except Exception as e:
            response={
                "status":0,
                "data":{
                    "message":"Error occured. {}".format(e)}
            }
            return JsonResponse(response)
    
    def put(self, request, url, format=None):
        locked_savings = self.get_savings(url)
        serializer = LockedSavingSerializer(locked_savings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, url, format=None):
        try:
            goal = self.get_savings(url)
            goal.delete()
            response={
                "status":1,
                "data":{
                    "message":"Goal saving deleted successfuly",
                    }
                }
            return Response(response)

        except Exception as e:
            response={
                "status":0,
                "data":{
                    "message":"Error occured. {}".format(e)}
            }
            return JsonResponse(response)
