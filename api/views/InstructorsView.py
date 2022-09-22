# Response and permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# for rendering errors
from api.renderers import UserRenderer

# Models
from api.models import Course, Instructors, User

# serializer
from api.serializer.UserSerializer import UserProfileSerializer
from api.serializer.InstructorsSerializer import TeacherInstructorsSerializer, AdminInstructorsSerializer,\
    PostInstructorsSerializer

Roles = {'Admin': 'admin', 'Teacher': 'teacher', 'Student': 'student'}


class UserInstructorsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        """This function provides Assigned and UnAssigned Instructors View to the Admin."""
        if request.user.usertype == Roles['Admin']:
            courseid = request.GET.get('courseid')

            teachers = User.objects.filter(usertype='teacher').all()
            assigned = list(Instructors.objects.filter(
                courseid=courseid).values_list('teacherid', flat=True))

            assignedTeacher = []
            unassignedTeacher = []

            for teacher in teachers:
                if teacher.id in assigned:
                    assignedTeacher.append(teacher)
                else:
                    unassignedTeacher.append(teacher)

            AssignedTeacher = UserProfileSerializer(
                data=assignedTeacher, many=True)
            AssignedTeacher.is_valid()

            NotAssignedTeachers = UserProfileSerializer(
                data=unassignedTeacher, many=True)
            NotAssignedTeachers.is_valid()

            return Response({"assigned": list(AssignedTeacher.data), "unassigned": list(NotAssignedTeachers.data)},
                            status=status.HTTP_200_OK)

        if request.user.usertype == Roles['Teacher']:
            assigned = Instructors.objects.filter(
                teacherid=request.user.id)
            serializer = TeacherInstructorsSerializer(
                data=assigned, many=True)
            serializer.is_valid()
            return Response({"assigned": list(serializer.data)},
                            status=status.HTTP_200_OK)

        if request.user.usertype == Roles['Student']:
            courses = Instructors.objects.all()
            serializer = AdminInstructorsSerializer(data=courses, many=True)

            return Response({"enrolls": serializer.data},
                            status=status.HTTP_200_OK)

        return Response({'error': "You are not authorized!"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        """This function Assign the Course to requested Teacher."""
        if request.user.usertype == Roles['Admin']:
            serializer = PostInstructorsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            Course.objects.get(id=request.data['courseid']).instructors.add(
                User.objects.get(id=request.data['teacherid']))
            return Response({"msg": "Course Assigned to Teacher."}, status=status.HTTP_201_CREATED)
        return Response({'error': "Only Admins can add and delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        """This function Unassign the Course from requested Teacher."""
        if request.user.usertype == Roles['Admin']:
            enrolled = Instructors.objects.filter(
                teacherid=request.data['teacherid'], courseid=request.data['courseid'])
            if enrolled:
                enrolled.delete()
                return Response({'msg': 'Course Assignment deleted successfully!'}, status=status.HTTP_200_OK)
            return Response({'error': 'Course Assignment Not Found!'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)
