from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
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
            serializers.save(user = request.user)
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class GoalDescription(APIView):
    permission_classes = (IsAuthenticated,)
    def get_goal(self, pk):
        try:
            return Goal.objects.get(pk=pk)
        except Goal.DoesNotExist:
            return Http404

    def get(self, request, pk, format=None):
        goal = self.get_goal(pk)
        serializers = GoalSerializer(goal)
        return Response(serializers.data)