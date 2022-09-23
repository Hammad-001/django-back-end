# importing serializer
from rest_framework import serializers

# Email and Username Validator
from rest_framework.validators import UniqueValidator

# model import
from api.models import User

# Password Reset Via Email
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# import for sending Email
from api.Utils import Utils

# ------------------------------------Serializers------------------------------------ #


class UserRegistrationSerializer(serializers.ModelSerializer):
    # Serializer For User Registration

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email already exists!")])
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()


    class Meta:
        model = User
        fields = ['id', 'email', 'password',
                  'first_name', 'last_name', 'cnic', 'usertype']

    def validate(self, attrs):
        if attrs.get('usertype') == 'admin':
            user = User.objects.create_superuser(**attrs)
        else:
            user = User.objects.create_user(**attrs)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    # For User Profile
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'cnic', 'usertype']
        read_only_fields = fields

class UserChangePasswordSerializer(serializers.ModelSerializer):
    # For User Password Change
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['password']

    def validate(self, attrs):
        user = self.context.get('user')
        password = attrs.get('password')
        user.set_password(password)
        user.save()
        return attrs


class SendEmailTOUserForPasswordResetSerializer(serializers.ModelSerializer):
    # For Sending Password Reset Email
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.get(email=email)
        if user != None:
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/reset/'+uid+'/'+token
            body = 'Click following link to reset your password '+link
            data = {
                'subject': "Password Reset Email",
                'body': body,
                'to_email': [user.email],
            }
            Utils.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError("User does not exists!")


class UserPasswordRestSerializer(serializers.ModelSerializer):
    # For Validating email password reset request
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['password']

    def validate(self, attrs):
        try:
            uid = self.context.get('uid')
            token = self.context.get('token')
            password = attrs.get('password')
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError(
                    "Token is not Valid or Expired.")
            user.set_password(password)
            user.save()
            return super().validate(attrs)
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not Valid or Expired.")