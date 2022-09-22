# Response and permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# for rendering errors
from api.renderers import UserRenderer

# Models
from api.models import Attendance, Enrolled

# serializer
from api.serializer.EnrollmentSerializer import TeacherCourseViewSerializer
from api.serializer.AttendanceSerializer import UserAttendanceSerializer, UserAttendanceSerializerNew

Roles = {'Admin': 'admin', 'Teacher': 'teacher', 'Student': 'student'}


class UserAttendanceView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        if request.user.usertype == Roles['Student']:
            attendance = Attendance.objects.select_related('courseid').filter(
                studentid=request.user.id, courseid=request.GET.get('courseid'))
            serializer = UserAttendanceSerializerNew(attendance, many=True)
            return Response({"attendance": serializer.data}, status=status.HTTP_200_OK)

        if request.user.usertype == Roles['Teacher']:
            enrolled = Enrolled.objects.select_related(
                'studentid').filter(courseid=request.GET.get('courseid'))
            serializer = TeacherCourseViewSerializer(enrolled, many=True)
            return Response({"enrolled": list(serializer.data)}, status=status.HTTP_200_OK)

        return Response({'error': "You are not authorized!"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if request.user.usertype == Roles['Teacher']:
            for data in request.data['enrolled']:
                data['courseid'] = int(request.data['courseid'])
                data['studentid'] = int(data['studentid']['id'])
            serializer = UserAttendanceSerializer(
                data=request.data['enrolled'], many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"msg": "Attendance Marked!"}, status=status.HTTP_201_CREATED)

        return Response({'error': "Only Teachers can add data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        if request.user.usertype == Roles['Teacher']:
            try:
                enrolled = Attendance.objects.filter(id=request.data['id'])
            except:
                return Response({'error': "Enrollment Id Not Found!"}, status=status.HTTP_404_NOT_FOUND)

            if enrolled:
                enrolled.delete()

                return Response({'msg': 'Enrollment deleted successfully!'}, status=status.HTTP_200_OK)

            return Response({'error': 'Enrollment Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only students can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)
