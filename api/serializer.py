# importing serializer
from dataclasses import fields
from rest_framework import serializers

# model import
from api.models import Attendance, Course, Enrolled, Instructors, User

# import for sending Email
from api.Utils import Utils
import datetime

# Email and USername Validator
from rest_framework.validators import UniqueValidator

# Password Reset Via Email
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


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

# For Sending Password Reset Email


class SendEmailTOUserForPasswordResetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
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

# For Validating email password reset request


class UserPasswordRestSerializer(serializers.ModelSerializer):
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
            print(user.password)
            user.save()
            return super().validate(attrs)
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not Valid or Expired.")


class UserCourseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = Course
        fields = ['id', 'code', 'name']

class UserCourseDetailViewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    enrolled = UserProfileSerializer(many=True)
    instructors = UserProfileSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'instructors', 'enrolled']

class UserEnrollSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    studentid = UserProfileSerializer()

    class Meta:
        model = Enrolled
        fields = ['id', 'courseid', 'studentid', 'result', "year"]


class UserInstructorsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    courseid = UserCourseSerializer()
    teacherid = UserProfileSerializer()

    class Meta:
        model = Instructors
        fields = ['id', 'courseid', 'teacherid', 'year']


class UserAttendanceSerializerNew(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'date', 'isabsent']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['studentid'] = UserProfileSerializer(instance.studentid).data
        rep['courseid'] = UserCourseSerializer(instance.courseid).data
        return rep


class UserAttendanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    date = serializers.DateField(required=False)

    class Meta:
        model = Attendance
        fields = ['id', 'courseid', 'studentid', 'isabsent', 'date']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['studentid'] = UserProfileSerializer(instance.studentid).data
        rep['courseid'] = UserCourseSerializer(instance.courseid).data
        return rep

    def validate(self, attrs):
        studentid = attrs.get("studentid")
        courseid = attrs.get("courseid")

        notstudent = (User.objects.get(id=studentid.id).usertype != "student")
        notenrolled = (not Enrolled.objects.filter(
            studentid=studentid, courseid=courseid))

        if notstudent or notenrolled:
            raise serializers.ValidationError(
                "Attendance of only enrolled Students can be marked!")

        date = Attendance.objects.filter(
            courseid=courseid, studentid=studentid, date=datetime.date.today())

        if date:
            raise serializers.ValidationError(
                "Cannot Add Attendance of Same Course Twice in a day!")
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['date'] = datetime.date.today()
        return super().create(validated_data)
