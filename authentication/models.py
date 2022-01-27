from distutils.command.upload import upload
# from re import T
import pyotp
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
# Create your models here.

class MyUser(AbstractBaseUser):
  user_id = models.UUIDField(null=True)
  phone_number = models.CharField(max_length=15, unique=True)
  password = models.CharField(max_length=300)
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  username = models.CharField(max_length=50, blank=True, null=True)
  id_number = models.IntegerField(null=True)
  email = models.EmailField(blank=True, null=True)
  is_superuser = models.BooleanField(default=False)
  is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into our admin site.'
    )
  is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. '
    )
  id_pic_front = models.ImageField(upload_to = 'id_image/',blank = True, null = True)
  id_pic_back = models.ImageField(upload_to = 'id_image/', blank = True, null = True)
  is_verified = models.BooleanField(default=False,
    help_text='Tells whether a user is verified or not using their ID',
    )
  date_added = models.DateTimeField(auto_now_add=True)
  date_updated = models.DateTimeField(blank=True, null=True)
  url = models.URLField(max_length=100, blank=True, null=True)
  visibility = models.IntegerField(default=1,blank=True, null=True)
  referral_code = models.CharField(max_length=300, blank=True, null=True)
  refered_by = models.IntegerField(blank=True, null=True)


  objects = UserManager()
  
  USERNAME_FIELD = 'phone_number'
  REQUIRED_FIELDS = []

  class Meta:
    ordering = ['-date_added']

  def __str__(self):
    return self.first_name + self.last_name

  def authenticate(self, otp):
    """This method authenticates the given OTP"""
    provided_otp = 0
    try:
      provided_otp = int(otp)
    except:
      return False
    #Here we are using Time Based OTP. The interval is 300 seconds.
    #otp must be provided within this interval or it's invalid
    t = pyotp.TOTP(self.key, interval=300)
    return t.verify(provided_otp)