from django.db import models
from django.conf import settings

# Create your models here.

class Goal(models.Model):
  goal_id = models.UUIDField(null=True)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  thumbnail = models.ImageField(upload_to = 'goals')
  goal_name = models.CharField(max_length=50, null=False)
  amount = models.IntegerField(default=0)
  start_date = models.DateTimeField(auto_now_add=True)
  maturity_date = models.DateField('maturity_date')
  daily_reminder = models.BooleanField(default=True)
  auto_save = models.BooleanField(default=False)
  date_updated = models.DateTimeField(null=True)

