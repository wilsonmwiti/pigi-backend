from django.db import models

from authentication.models import MyUser

# Create your models here.

class Transactions(models.Model):
  transaction_id = models.CharField(max_length=20,unique=True)
  transaction_time = models.CharField(max_length=50)
  transaction_amount = models.DecimalField(max_digits=8,decimal_places=2)
  bill_reference_number = models.CharField(max_length=50,null=True,blank=True)
  org_account_balance = models.CharField(max_length=50)
  msisdn = models.CharField(max_length=16)
  first_name = models.CharField(max_length=50,null=True,blank=True)
  middle_name = models.CharField(max_length=50,null=True,blank=True)
  last_name = models.CharField(max_length=50,null=True,blank=True)
  status = models.IntegerField(default=0)
  status_reason = models.CharField(max_length=200,blank=True, null=True)

class LockedSaving(models.Model):
  user = models.ForeignKey(MyUser, on_delete=models.CASCADE )
  amount = models.IntegerField()
  maturity_date = models.DateTimeField()
  date_added = models.DateTimeField(auto_now_add=True)
  