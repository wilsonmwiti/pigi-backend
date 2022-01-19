# from django.db.models.signals import pre_save
# from django.dispatch import receiver
# from .models import MyUser
# import pyotp

# def generate_key():
#   "User otp key generator"
#   key = pyotp.random_base32()
#   if is_unique(key):
#     return key
#   generate_key()

# def is_unique(key):
#   try:
#     MyUser.objects.get(key=key)
#   except MyUser.DoesNotExist:
#     return True
#   return False

# @receiver(pre_save, sender = MyUser)
# def create_key(sender,instance, **kwargs):
#   """This creates a key for users that do not have keys"""
#   if not instance.key:
#     instance.key = generate_key()
