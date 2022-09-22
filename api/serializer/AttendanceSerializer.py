# importing serializer
from rest_framework import serializers

# model import
from api.models import Attendance, Enrolled, User

# Other Serializers
from api.serializer.CourseSerializer import SimpleCourseSerializer

# other import
import datetime

# ------------------------------------Serializers------------------------------------ #


class UserAttendanceSerializerNew(serializers.ModelSerializer):
    # For Student Enrolled Subject's Attendance View

    courseid = SimpleCourseSerializer()

    class Meta:
        model = Attendance
        fields = ['id', 'courseid', 'date', 'isabsent']


class UserAttendanceSerializer(serializers.ModelSerializer):
    # Complete Attendance Serializer

    id = serializers.IntegerField(read_only=True)
    date = serializers.DateField(required=False)

    class Meta:
        model = Attendance
        fields = ['id', 'courseid', 'studentid', 'isabsent', 'date']

    def validate(self, attrs):
        studentid = attrs.get("studentid")
        courseid = attrs.get("courseid")
        attrs['date'] = datetime.datetime.today()

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
