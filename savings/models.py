from email.policy import default
from django.db import models
from django.conf import settings

# Create your models here.
class GeneralWallet(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  amount = models.IntegerField(default=0)

class Goal(models.Model):
  # class GoalStatus(models.IntegerChoices):
  #   PENDING = 0
  #   DONE = 1
  STATUS_CHOICES = (
      (0, 'Good'),
      (1, 'Bad'),
      (2, 'Excellent')
  )

  goal_id = models.UUIDField(null=True)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  thumbnail = models.ImageField(upload_to = 'goals', default = 'goals/pigibank-default.png')
  goal_name = models.CharField(max_length=50, null=False)
  target_amount = models.IntegerField(null=False, default = 0)
  current_saving = models.IntegerField(default=0)
  start_date = models.DateTimeField(auto_now_add=True)
  maturity_date = models.DateTimeField('maturity_date')
  daily_reminder = models.BooleanField(default=True)
  auto_save = models.BooleanField(default=False)
  daily_amount = models.IntegerField(default = 0 )
  date_updated = models.DateTimeField(null=True)
  status = models.IntegerField(default=0, choices=STATUS_CHOICES)


class LockedSavings(models.Model):
  DURATION_OPTION = (
      (3, 'Quarterly'),
      (6, 'Semi Anually'),
      (12, 'Anually')
  )
  STATUS_CHOICES = (
    (0, 'Pending'),
    (1, 'In Progress'),
    (2, 'Finished')
  )
  savings_id = models.UUIDField(null=False)
  thumbnail = models.ImageField(upload_to = 'locked_savings', default = 'pigibank-default.png')
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  item_name = models.CharField(max_length=50,null=False )
  principal_deposit = models.IntegerField(default=0)
  date_added = models.DateTimeField(auto_now_add=True)
  date_updated = models.DateTimeField(null=True)
  duration = models.IntegerField(null = False, choices=DURATION_OPTION)
  current_total = models.IntegerField(default=0)
  status = models.IntegerField(default=0, choices=STATUS_CHOICES)
