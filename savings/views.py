import uuid
from django.shortcuts import render
from django.http import Http404
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
# Create your views here.

class  GoalList(APIView):
  permission_classes = [IsAuthenticated,]
  def get(self, request, format=None):
    try:
        all_goals = Goal.objects.filter(user = request.user)
        print(all_goals)
    except Goal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializers = GoalSerializer(all_goals, many=True)
    return Response(serializers.data)

  def post(self, request, format=None):
        serializers = GoalSerializer(data=request.data)
        if serializers.is_valid():      
            print("USER ID: ",request.user)
            goal_id = uuid.uuid4()
            serializers.save(user = request.user, goal_id = goal_id)
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class GoalDescription(APIView):
    permission_classes = (IsAuthenticated,)
    def get_goal(self, uuid):
        try:
            return Goal.objects.get(goal_id=uuid)
        except Goal.DoesNotExist:
            return Http404

    def get(self, request, url, format=None):
        goal = self.get_goal(url)
        serializers = GoalSerializer(goal)
        return Response(serializers.data)
    
    def put(self, request, url, format=None):
        goal = self.get_goal(url)
        serializer = GoalSerializer(goal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, url, format=None):
        goal = self.get_goal(url)
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class  LockedSavingsList(APIView):
    '''An api that gets a list of all locked savings for a particular user'''
    permission_classes = [IsAuthenticated,]
    def get(self, request, format=None):
        try:
            all_locked = LockedSavings.objects.filter(user = request.user)
            print(all_locked)
        except LockedSavings.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializers = LockedSavingSerializer(all_locked, many=True)
        return Response(serializers.data)

    def post(self, request, format=None):
        serializers = LockedSavingSerializer(data=request.data)
        if serializers.is_valid():
            savings_id = uuid.uuid4()
            serializers.save(user = request.user , savings_id = savings_id)
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class LockedSavingsDesc(APIView):
    permission_classes = (IsAuthenticated,)
    def get_savings(self, uuid):
        try:
            return LockedSavings.objects.get(savings_id=uuid)
        except LockedSavings.DoesNotExist:
            return Http404

    def get(self, request, url, format=None):
        locked_savings = self.get_savings(url)
        serializers = LockedSavingSerializer(locked_savings)
        return Response(serializers.data)
    
    def put(self, request, url, format=None):
        locked_savings = self.get_savings(url)
        serializer = LockedSavingSerializer(locked_savings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, url, format=None):
        goal = self.get_goal(url)
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
