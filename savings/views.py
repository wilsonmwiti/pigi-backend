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
from .models import Goal
from .serializers import GoalSerializer
# Create your views here.

class  GoalList(APIView):
  permission_classes = [IsAuthenticated]
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