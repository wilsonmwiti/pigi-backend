from multiprocessing import context
from pyexpat import model
from rest_framework import serializers
from .models import MyUser
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
import random
import uuid
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

#   @classmethod
#   def get_token(cls, user):
#     token = super(MyTokenObtainPairSerializer, cls).get_token(user)

#     # Add custom claims
#     token['phonenumber'] = user.phone_number
#     return token
def generate_unique_username(firstname,lastname):
  first_letter = firstname[0]
  # space_index = lastname.find(" ")
  surname = lastname[0:-1]
  number = random.randrange (1,999)
  lower = 'abcdefghijklmnopqrstuvwxyz'
  upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  length = 4
  all = lower+upper+str(number)
  randomString=''.join(random.sample(all, length))
  username = first_letter+'_'+surname+randomString
  if MyUser.objects.filter(username = username).exists():
    new_number =random.randrange(1, 999)
    username = "".join([first_letter, surname, str(new_number)])
    return username
  return username


class CustomAuthToken(ObtainAuthToken):
  def post(self, request, *args, **kwargs):
    serializer = self.serializer_class(data=request.data, context = {'request': request})
    print(serializer)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    print (user)
    token, created = Token.objects.get_or_create(user=user)
    return Response({
      'token': token.key,
      'user_id': user.pk,
      'phone_number': user.phone_number
    })



class RegisterSerializer(serializers.ModelSerializer):
  phone_number = serializers.CharField(
    required = True, 
    validators = [UniqueValidator(queryset=MyUser.objects.all())]
    )
  first_name = serializers.CharField(max_length = 50)
  last_name = serializers.CharField(max_length = 50)
  password = serializers.CharField(write_only=True, required=True)
  

  class Meta:
    model = MyUser
    fields = ('phone_number', 'password', 'first_name', 'last_name', 'id_number')
    extra_kwargs = {
        'first_name': {'required': True},
        'last_name': {'required': True},
        'phone_number': {'required':True},
        
    }

 
    def create(self, validated_data):
      first_name=validated_data['first_name']
      last_name=validated_data['last_name']

      # ##Generate a unique username
      # lower = 'abcdefghijklmnopqrstuvwxyz'
      # upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      # number = '1234567890'
      # length = 7
      # all = lower+upper+number
      # randomString=''.join(random.sample(all, length))
      # username = first_name+'_'+last_name+'_'+randomString
      username = generate_unique_username(first_name,last_name)
      
      #Create a user instance
      user = MyUser.objects.create(
        phone_number=validated_data['phone_number'],
        first_name=first_name,
        last_name=last_name,
        id_number = validated_data['id_number'],
        username = username,
        is_active = True,   
      )
      
      user.set_password(validated_data['password'])
      user.save()
      return user

class RegisterSubaccountSerializer(serializers.Serializer):
  first_name = serializers.CharField(max_length = 50)
  last_name = serializers.CharField(max_length = 100)
  thumbnail = serializers.ImageField()

  def create(self, validated_data):
    firstname=validated_data['first_name']
    lastname=validated_data['last_name']
    username = generate_unique_username(firstname, lastname)
    user = MyUser.objects.create(
      thumbnail = validated_data['thumbnail'],
      first_name= firstname,
      last_name = lastname,
      username = username,
    )
    return user
  
  def update(self, instance, validated_data):
    instance.first_name = validated_data.get('first_name', instance.email)
    instance.last_name = validated_data.get('last_name', instance.content)
    instance.thumbnail = validated_data.get('thumbnail', instance.created)
    instance.save()
    return instance

  # def generate_unique_username(firstname,lastname):
  #   first_letter = firstname[0]
  #   space_index = lastname.find(" ")
  #   three_letters_surname = lastname[space_index + 1:space_index + 4]
  #   number = random.randrange (1,999)
  #   username = "".join([first_letter, three_letters_surname, str(number)])

  #   if MyUser.objects.filter(username = username).exists():
  #     new_number =random.randrange(1, 999)
  #     username = "".join([first_letter, three_letters_surname, str(new_number)])
  #     return username
  #   return username
  


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = MyUser
    fields = ['id','user_id','first_name','last_name','username','id_number','thumbnail', 'date_added']