# importing serializer
from rest_framework import serializers

# model import
from api.models import Instructors

# Other Serializers
from api.serializer.UserSerializer import UserProfileSerializer
from api.serializer.CourseSerializer import UserCourseSerializer

# ------------------------------------Serializers------------------------------------ #


class AdminInstructorsSerializer(serializers.ModelSerializer):
    # For  Admin's Course View

    id = serializers.IntegerField(read_only=True)
    courseid = UserCourseSerializer()
    teacherid = UserProfileSerializer()

    class Meta:
        model = Instructors
        fields = ['id', 'courseid', 'teacherid', 'year']


class PostInstructorsSerializer(serializers.ModelSerializer):
    # For Creating Instructors

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Instructors
        fields = ['id', 'courseid', 'teacherid', 'year']

    def validate(self, attrs):
        if Instructors.objects.filter(courseid=attrs.get('courseid')):
            raise serializers.ValidationError(
                'Only one Teacher can teach a course in every year.')
        return super().validate(attrs)


class TeacherInstructorsSerializer(serializers.ModelSerializer):
    # Courses' View For Teachers

    id = serializers.IntegerField(read_only=True)
    courseid = UserCourseSerializer()
    teacherid = UserProfileSerializer()

    class Meta:
        model = Instructors
        fields = ['id', 'courseid', 'teacherid', 'year']
