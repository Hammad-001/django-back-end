# importing serializer
from rest_framework import serializers

# model import
from api.models import Enrolled

# Other Serializers
from api.serializer.UserSerializer import UserProfileSerializer

# ------------------------------------Serializers------------------------------------ #

class UserEnrollSerializer(serializers.ModelSerializer):
    # Student Enrollments Serializer
    
    id = serializers.IntegerField(read_only=True)
    result = serializers.IntegerField(required=False)

    class Meta:
        model = Enrolled
        fields = ['id', 'courseid', 'studentid', 'result', "year"]

class TeacherCourseViewSerializer(serializers.ModelSerializer):
    # For Course View of Teacher ONLY

    id = serializers.IntegerField(read_only=True)
    studentid = UserProfileSerializer()

    class Meta:
        model = Enrolled
        fields = ['id', 'studentid', 'result', "year"]
