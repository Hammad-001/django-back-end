# Response and permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# from django
from django.db.models import Q

# for rendering errors
from api.renderers import UserRenderer

# Models
from api.models import Course, Enrolled

# serializers
from api.serializer.EnrollmentSerializer import TeacherCourseViewSerializer
from api.serializer.CourseSerializer import UserCourseDetailViewSerializer, UserCourseSerializer,\
    StudentCourseViewSerializer, SimpleCourseSerializer

Roles = {'Admin': 'admin', 'Teacher': 'teacher', 'Student': 'student'}


class UserCourseView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """This function provides different Courses view depending on for their Role."""
        if request.user.usertype == Roles['Admin']:
            if request.GET.get('courseid'):
                enrolledStudents = Course.objects.prefetch_related('instructors', 'enrolled').filter(id=request.GET.get(
                    'courseid'))
                enrolledStudentSerializer = UserCourseDetailViewSerializer(
                    data=enrolledStudents, many=True)
                enrolledStudentSerializer.is_valid()
                return Response({"coursedetail": enrolledStudentSerializer.data}, status=status.HTTP_200_OK)
            courses = Course.objects.prefetch_related('instructors').all()
            coursesSerializer = UserCourseSerializer(
                data=courses, many=True)
            coursesSerializer.is_valid()
            return Response({"courses": list(coursesSerializer.data)},
                            status=status.HTTP_200_OK)

        if request.user.usertype == Roles['Student']:
            allCourses = Course.objects.prefetch_related('instructors').all()
            enrolled = Enrolled.objects.filter(
                studentid=request.user.id)
            result = list(enrolled.values_list('courseid', 'result'))
            rem = list(enrolled.values_list('courseid', flat=True))

            enrolledCourses = []
            unenrolledCourses = []
            for course in allCourses:
                if course.id in rem:
                    course.result = [res[1]
                                     for res in result if course.id == res[0]][0]
                    enrolledCourses.append(course)
                else:
                    unenrolledCourses.append(course)
            enrolledSerializer = StudentCourseViewSerializer(
                enrolledCourses, many=True)
            unenrolledSerializer = UserCourseSerializer(
                unenrolledCourses, many=True)

            return Response({"enrolled": list(enrolledSerializer.data), 'courses': list(unenrolledSerializer.data)},
                            status=status.HTTP_200_OK)

        if request.user.usertype == Roles['Teacher']:
            allenrolled = Enrolled.objects.select_related(
                'studentid').filter(courseid=request.GET.get('courseid'))
            enrolledSerializer = TeacherCourseViewSerializer(
                allenrolled, many=True)
            return Response({"enrolled": list(enrolledSerializer.data)}, status=status.HTTP_200_OK)

    def post(self, request):
        """This function provides create course functionality."""
        if request.user.usertype == Roles['Admin']:
            getCourse = Course.objects.filter(
                Q(code=request.data['code']) or Q(name=request.data['name']))
            if getCourse:
                return Response({'code': "Course with this name or code Already Exists!"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = SimpleCourseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"msg": "Course is Registered."}, status=status.HTTP_201_CREATED)
        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        """This function provides update course functionality."""
        if request.user.usertype == Roles['Admin']:
            course = Course.objects.get(pk=request.data['id'])
            if course:
                serializer = SimpleCourseSerializer(
                    course, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({"msg": "Course Updated successfully."}, status=status.HTTP_200_OK)

            return Response({'error': 'Course Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        """This function removes the course using its id. Only admins can access this feature."""
        if request.user.usertype == Roles['Admin']:
            course = Course.objects.filter(id=request.data['id'])
            if course:
                course.delete()

                return Response({'msg': 'Course deleted successfully!'}, status=status.HTTP_200_OK)

            return Response({'error': 'Course Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)
