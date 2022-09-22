# Response and permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# for rendering errors
from api.renderers import UserRenderer

# Models
from api.models import Attendance, Enrolled

# serializers
from api.serializer.EnrollmentSerializer import UserEnrollSerializer

Roles = {'Admin': 'admin', 'Teacher': 'teacher', 'Student': 'student'}


class UserEnrollView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        if request.user.usertype == Roles['Student']:
            request.data['studentid'] = request.user.id
            if Enrolled.objects.filter(courseid=request.data["courseid"], studentid=request.data['studentid']):
                return Response({"msg": "Enrollment Already Exists!"}, status=status.HTTP_200_OK)
            serializer = UserEnrollSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"msg": "Enrollment is Registered."}, status=status.HTTP_201_CREATED)

        if request.user.usertype == Roles['Teacher']:
            if request.data['result'] > 100 or request.data['result'] < 0:
                return Response({"msg": "Marks should be in range 0-100."}, status=status.HTTP_201_CREATED)
            serializer = UserEnrollSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({'error': "Only Students can add and delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        """This function provides the functionality to Update the marks of students. It can only be modified by teachers."""
        if request.user.usertype == Roles['Teacher']:
            invalidMarks = False
            for obj in request.data:
                if obj['result'] == None or obj['result'] > 100 or obj['result'] < 0 or obj['result'] == "":
                    invalidMarks = True
            if not invalidMarks:
                for obj in request.data:
                    enrolledobject = Enrolled.objects.get(pk=obj['id'])
                    if enrolledobject:
                        enrolledobject.result = obj['result']
                        enrolledobject.save(update_fields=['result'])
                return Response({'msg': 'Marks added successfully!'}, status=status.HTTP_200_OK)
            return Response({'msg': 'Marks must be within range 0-100!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "Only Teachers can add and delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        """This function provides the functionality to UnEnroll subjects. It can only be modified by teachers."""
        if request.user.usertype == Roles['Student']:
            enrolled = Enrolled.objects.filter(
                courseid=request.data['id'], studentid=request.user.id)
            attendance = Attendance.objects.filter(
                courseid=request.data['id'], studentid=request.user.id)

            if enrolled or attendance:
                enrolled.delete()
                if attendance:
                    attendance.delete()

                return Response({'msg': 'Enrollment deleted successfully!'}, status=status.HTTP_200_OK)

            return Response({'error': 'Enrollment Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only students can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)
