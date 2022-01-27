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
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

#   @classmethod
#   def get_token(cls, user):
#     token = super(MyTokenObtainPairSerializer, cls).get_token(user)

#     # Add custom claims
#     token['phonenumber'] = user.phone_number
#     return token
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

    ##Generate a unique username
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    number = '1234567890'
    length = 7
    all = lower+upper+number
    randomString=''.join(random.sample(all, length))
    username = first_name+'_'+last_name+'_'+randomString
    #Create a user instance
    user = MyUser.objects.create(
      phone_number=validated_data['phone_number'],
      first_name=validated_data['first_name'],
      last_name=validated_data['last_name'],
      id_number = validated_data['id_number'],
      username = username,       
    )
    
    user.set_password(validated_data['password'])
    user.save()

    return user

class UserSerializer(serializers.Serializer):
  class Meta:
    model = MyUser
    fields = ['first_name','last_name','username','password','id_number']