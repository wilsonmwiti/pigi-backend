from django.db import models
from django.conf import settings
from authentication.models import MyUser

# Create your models here.


class Transactions(models.Model):
    TRANSACTION_TYPE = (
        ('D', 'Deposit'),
        ('W', 'Withdraw'),
        ('T', 'Transfer'),
    )
    TRANSACTION_STATUS = (
        (1032, 'Cancelled'),
        (0, 'Complete'),
        (1, 'Pending')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True)
    transaction_id = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=TRANSACTION_TYPE, null=True)
    transaction_time = models.DateTimeField(auto_now_add=True)
    transaction_amount = models.DecimalField(max_digits=8, decimal_places=2)
    mpesa_receipt_number = models.CharField(
        max_length=50, null=True, blank=True)
    status = models.IntegerField(default=1, choices=TRANSACTION_STATUS)
    description = models.CharField(max_length=50, null=True)
    created_at = models.DateField(auto_now_add=True)


class LockedSaving(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    amount = models.IntegerField()
    maturity_date = models.DateTimeField()
    date_added = models.DateTimeField(auto_now_add=True)
