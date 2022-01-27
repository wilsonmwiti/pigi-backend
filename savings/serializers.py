from django.forms import models
from rest_framework import serializers
from .models import Goal

class GoalSerializer(serializers.ModelSerializer):

  class Meta:
    model = Goal
    fields = ('id','goal_id','thumbnail','goal_name','amount','maturity_date','daily_reminder',
    'auto_save')

  