# importing serializer
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
from django.contrib.auth.models import Group

from django.db.models import Q

# For User Registration


class UserRegistrationSerializer(serializers.ModelSerializer):
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
        usertype = attrs.get('usertype')

        if usertype not in ['admin', 'student', 'teacher']:
            raise serializers.ValidationError("Invalid User Type!")

        return attrs

    def create(self, validated_data):

        if validated_data['usertype'] == 'admin':
            user = User.objects.create_superuser(**validated_data)
        else:
            user = User.objects.create_user(**validated_data)

        return user


# For User Login


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'password']

# For User Profile


class UserProfileSerializer(serializers.ModelSerializer):
    usertype = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name',
                  'last_name', 'cnic', 'usertype']

# For User Password Change


class UserChangePasswordSerializer(serializers.ModelSerializer):
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
            body = 'Click following link to reset your password '+link + \
                "\n If you donot find email, kindly check spam folder."
            data = {
                'subject': "Password Reset Email",
                'body': body,
                'to_email': [user.email],
            }
            Utils.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError("User doesnot exists!")

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


class UserEnrollSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Enrolled
        fields = ['id', 'courseid', 'studentid', 'result', "year"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['studentid'] = UserProfileSerializer(instance.studentid).data
        rep['courseid'] = UserCourseSerializer(instance.courseid).data
        return rep

class UserAttendanceSerializerNew(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id','date', 'isabsent']
        
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


class UserInstructorsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Instructors
        fields = ['id', 'teacherid', 'courseid']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['teacherid'] = UserProfileSerializer(instance.teacherid).data
        rep['courseid'] = UserCourseSerializer(instance.courseid).data
        return rep


class UserInstructors(serializers.Serializer):
    id= serializers.IntegerField()
    first_name = serializers.CharField()

