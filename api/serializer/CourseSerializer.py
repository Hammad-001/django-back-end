# importing serializer
from rest_framework import serializers

# model import
from api.models import Course

# Other Serializers
from api.serializer.UserSerializer import UserProfileSerializer

# ------------------------------------Serializers------------------------------------ #


class SimpleCourseSerializer(serializers.ModelSerializer):
    # Course Serializer For simple Fields

    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = Course
        fields = ['id', 'code', 'name']


class UserCourseSerializer(serializers.ModelSerializer):
    # Course Serializer For simple Fields with instructors

    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField()
    name = serializers.CharField()
    instructors = UserProfileSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'instructors']


class StudentCourseViewSerializer(serializers.ModelSerializer):
    # Course Serializer for simple fields with instructors (and enrolled table's result)
    # For Student Courses View ONLY

    id = serializers.IntegerField(read_only=True)
    result = serializers.IntegerField()
    instructors = UserProfileSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'instructors', 'result']


class EnrolledCourseSerializer(serializers.ModelSerializer):
    # Course Serializer For simple Fields with enrollments

    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField()
    name = serializers.CharField()
    enrolled = UserProfileSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'enrolled']


class UserCourseDetailViewSerializer(serializers.ModelSerializer):
    # Complete Course Serializer with all fields

    id = serializers.IntegerField(read_only=True)
    enrolled = UserProfileSerializer(many=True)
    instructors = UserProfileSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'instructors', 'enrolled']
