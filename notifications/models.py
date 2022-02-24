from django.db import models
from django.conf import settings
# Create your models here.

class Notification(models.Model):

  MSG_CATEGORY = (
        ('S', 'Saving'),
        ('D', 'Deposit'),
        ('R', 'Reminder'),

  )
  
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  # category = models.CharField(max_length=1, choices=MSG_CATEGORY)
  is_read = models.BooleanField(default=False)
  isPositive = models.BooleanField(default=True)
  message = models.TextField(max_length=100)
  action=models.CharField(max_length=255, null=True)
  created_date = models.DateTimeField(auto_now_add=True)
  date_added = models.DateField(auto_now_add=True)

  class Meta:
    ordering = ['-created_date']