from time import strptime
from xmlrpc.client import DateTime
from django.forms import models
from rest_framework import serializers
from .models import GeneralWallet, Goal, LockedSavings
import datetime
# from datetime import date

# def days_between(d1, d2):
#     d1 = datetime.strptime(d1, "%Y-%m-%d")
#     d2 = datetime.strptime(d2, "%Y-%m-%d")
#     return abs((d2 - d1).days)

class GoalSerializer(serializers.ModelSerializer):
  status = serializers.CharField(source='get_status_display', required=False)

  class Meta:
    model = Goal
    fields = ('id', 'goal_id','user', 'thumbnail','goal_name','target_amount','maturity_date',
    'auto_save', 'status', 'start_date','daily_reminder', 'daily_amount')
    read_only_fields = ('id', 'goal_id', 'start_date','user', 'status','daily_reminder')
    
  
  def create(self, validated_data):
    auto_save = validated_data['auto_save']
    thumbnail = validated_data['thumbnail']
    today = datetime.datetime.now()
    print(today)
    start_time = today.strftime("%H:%M:%S.%f")
    input_maturity_date = validated_data['maturity_date']
    maturity_date = input_maturity_date.strftime("%y-%m-%d")
    daily_amount = validated_data['daily_amount']
  
    date_time_obj = maturity_date + " " + start_time

    final_maturity_date = datetime.datetime.strptime(date_time_obj, '%y-%m-%d %H:%M:%S.%f')

    print("NEW MATURITY DATE:", final_maturity_date)
    print("Maturity date: ",maturity_date)
    goal = Goal.objects.create(
      thumbnail = thumbnail,
      goal_name= validated_data['goal_name'],
      target_amount =  validated_data['target_amount'],

      maturity_date =  final_maturity_date,
      daily_amount = daily_amount,
      auto_save = auto_save,
    )
    return goal



class LockedSavingSerializer(serializers.ModelSerializer):
  class Meta:
    model = LockedSavings
    fields = ('id','user','savings_id','thumbnail','item_name','principal_deposit','date_added','date_updated',
    'duration','current_total')
    read_only_fields = ('id', 'savings_id', 'user')
    write_only_fields = ('id','user',)

class GeneralWalletSerializer(serializers.ModelSerializer):

  class Meta:
    model = GeneralWallet
    fields = ('user', 'amount')
    read_only_fields = ('user')

    