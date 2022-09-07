# Response and permissions
from xml.etree.ElementTree import QName
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# for auth
from django.contrib.auth import authenticate, logout
from django.contrib.auth.hashers import check_password

# for rendering errors
from api.renderers import UserRenderer

# serializers
from api.serializer import SendEmailTOUserForPasswordResetSerializer, UserAttendanceSerializer, UserChangePasswordSerializer, UserEnrollSerializer, UserInstructors, UserInstructorsSerializer,\
    UserLoginSerializer, UserPasswordRestSerializer, UserProfileSerializer, UserRegistrationSerializer,\
    UserCourseSerializer


# creating custom user auth token
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Course, Enrolled
from api.models import User, Attendance, Instructors

from django.db.models import Count


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        if request.user.usertype == 'admin':
            usertype = request.GET.get('usertype')
            if usertype == None or usertype == 'All':
                users = User.objects.all()
            else:
                try:
                    users = User.objects.filter(usertype=usertype)
                except:
                    return Response({'error': "UserType not provided!"}, status=status.HTTP_404_NOT_FOUND)

            serializer = UserRegistrationSerializer(users, many=True)
            return Response({'users': serializer.data},
                            status=status.HTTP_200_OK)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if request.user.usertype == 'admin':
            print("ADMIN")
            serializer = UserRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"msg": "User is Registered."},
                            status=status.HTTP_201_CREATED)
        else:
            print("error")
            return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, format=None):
        if request.user.usertype == 'admin':
            try:
                user = User.objects.get(pk=request.data['id'])
            except:
                user = False

            if user:
                serializer = UserRegistrationSerializer(
                    user, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"msg": "User Updated successfully."}, status=status.HTTP_200_OK)

            return Response({'error': 'User Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, format=None):
        if request.user.usertype == 'admin':
            try:
                user = User.objects.filter(id=request.data['id'])
            except:
                user = False

            if user:
                user.delete()
                return Response({'msg': 'User deleted successfully!'}, status=status.HTTP_200_OK)

            return Response({'error': 'User Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)

            if user != None:
                token = get_tokens_for_user(user)
                return Response({"token": token['access'],
                                 "usertype": user.usertype,
                                #  'firstname': user.first_name,
                                 #  'lastname': user.last_name,
                                 #  'cnic': user.cnic
                                 }, status=status.HTTP_200_OK)

            else:
                return Response({'error': ['Email or Password is not valid!']}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if check_password(request.data['password'], request.user.password):
            return Response({"errors": {"OldPassword": "New Password cannot be same as Old."}}, status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user})

        serializer.is_valid(raise_exception=True)

        return Response({"msg": "password changed successfully!"}, status=status.HTTP_200_OK)


class SendEmailToUserForPasswordRestView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendEmailTOUserForPasswordResetSerializer(
            data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response({"msg": "Password Reset link sent to given Provided Email"}, status=status.HTTP_200_OK)


class UserPasswordRestView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordRestSerializer(
            data=request.data, context={'uid': uid, 'token': token})

        serializer.is_valid(raise_exception=True)

        return Response({"msg": "password reset successfully."}, status=status.HTTP_200_OK)


class UserCourseView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if request.user.usertype in ['admin', 'student', 'teacher']:
            if request.GET.get('courseid') and request.user.usertype == 'admin':
                students = Enrolled.objects.filter(
                    courseid=request.GET.get('courseid'))
                StudentSerializer = UserEnrollSerializer(
                    data=students, many=True)
                teachers = Instructors.objects.filter(
                    courseid=request.GET.get('courseid'))
                TeacherSerializer = UserInstructorsSerializer(
                    data=teachers, many=True)
                StudentSerializer.is_valid()
                TeacherSerializer.is_valid()
                return Response({"students": list(StudentSerializer.data), 'teachers': list(TeacherSerializer.data)},
                                status=status.HTTP_200_OK)
            elif request.user.usertype == 'admin':
                courses = Course.objects.all()
                coursesSerializer = UserCourseSerializer(
                    data=courses, many=True)
                coursesSerializer.is_valid()
                return Response({"courses": list(coursesSerializer.data)},
                                status=status.HTTP_200_OK)

            if request.user.usertype == 'student':
                allenrolled = Enrolled.objects.filter(
                    studentid=request.user.id)
                rem = list(allenrolled.values_list('courseid', flat=True))

                courses = Course.objects.all().exclude(id__in=rem)
                enrolledSerializer = UserEnrollSerializer(
                    data=allenrolled, many=True)
                coursesSerializer = UserCourseSerializer(
                    data=courses, many=True)
                enrolledSerializer.is_valid()
                coursesSerializer.is_valid()
                return Response({"enrolled": list(enrolledSerializer.data), 'courses': list(coursesSerializer.data)},
                                status=status.HTTP_200_OK)

            if request.user.usertype == 'teacher':
                allenrolled = Enrolled.objects.filter(
                    courseid=request.GET.get('courseid'))
                enrolledSerializer = UserEnrollSerializer(
                    data=allenrolled, many=True)
                enrolledSerializer.is_valid()
                return Response({"enrolled": list(enrolledSerializer.data)}, status=status.HTTP_200_OK)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        if request.user.usertype == 'admin':
            code = request.data['code']
            name = request.data['name']
            getCode = Course.objects.filter(code=code)
            getName = Course.objects.filter(name=name)

            if getCode or getName:
                return Response({'code': "Course with this name or code Already Exists!"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = UserCourseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"msg": "Course is Registered."}, status=status.HTTP_201_CREATED)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, format=None):
        if request.user.usertype == 'admin':
            try:
                course = Course.objects.get(pk=request.data['id'])
            except:
                return Response({'error': "Course Not Found!"}, status=status.HTTP_404_NOT_FOUND)

            if course:
                serializer = UserCourseSerializer(
                    course, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({"msg": "Course Updated successfully."}, status=status.HTTP_200_OK)

            return Response({'error': 'Course Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, format=None):
        if request.user.usertype == 'admin':
            try:
                course = Course.objects.filter(id=request.data['id'])
            except:
                return Response({'error': "Course Id Not Found!"}, status=status.HTTP_404_NOT_FOUND)

            if course:
                course.delete()

                return Response({'msg': 'Course deleted successfully!'}, status=status.HTTP_200_OK)

            return Response({'error': 'Course Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserEnrollView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        if request.user.usertype == 'student':
            if Enrolled.objects.filter(courseid=request.data["courseid"],studentid=request.data['studentid']):
                return Response({"msg": "Enrollment Already Exists!"}, status=status.HTTP_200_OK)
            request.data['studentid'] = request.user.id
            serializer = UserEnrollSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"msg": "Enrollment is Registered."}, status=status.HTTP_201_CREATED)

        if request.user.usertype == 'teacher':
            serializer = UserEnrollSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({'error': "Only Students can add and delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self,request, format=None):
        if request.user.usertype == 'teacher':
            serializer = UserEnrollSerializer( data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'msg': 'Marks added successfully!'}, status=status.HTTP_200_OK)
        return Response({'error': "Only Teachers can add and delete data!"}, status=status.HTTP_401_UNAUTHORIZED)
            

    def delete(self, request, format=None):
        if request.user.usertype == 'student':
            try:
                enrolled = Enrolled.objects.filter(id=request.data['id'])
            except:
                return Response({'error': "Enrollment Id Not Found!"}, status=status.HTTP_404_NOT_FOUND)

            if enrolled:
                enrolled.delete()

                return Response({'msg': 'Enrollment deleted successfully!'}, status=status.HTTP_200_OK)

            return Response({'error': 'Enrollment Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only students can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserAttendanceView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        if request.user.usertype == 'student':
            try:
                attendance = Attendance.objects.filter(
                    studentid=request.user.id, courseid=request.data['courseid'])
            except:
                return Response({'error': "Invalid Course ID!"}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = UserAttendanceSerializer(attendance, many=True)

            return Response({"attendance": serializer.data},
                            status=status.HTTP_200_OK)

        if request.user.usertype == 'teacher':
            enrolled = Enrolled.objects.filter(
                courseid=request.GET.get('courseid'))

            serializer = UserEnrollSerializer(data=enrolled, many=True)
            serializer.is_valid()

            return Response({"enrolled": list(serializer.data)}, status=status.HTTP_200_OK)

        return Response({'error': "You are not authorized!"}, status=status.HTTP_401_UNAUTHORIZED)

    def checkduplicates(self, data):
        for index, value in enumerate(data):
            for jndex, jalue in enumerate(data):
                if (value['studentid'] == jalue['studentid'] and value['courseid'] == jalue['courseid']) and (index != jndex):
                    return True
        return False

    def post(self, request, format=None):
        if request.user.usertype == 'teacher':
            if self.checkduplicates(request.data):
                return Response({"msg": "Cannot add duplicate Attendance!"}, status=status.HTTP_403_FORBIDDEN)

            serializer = UserAttendanceSerializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"msg": "Attendance Marked!"}, status=status.HTTP_201_CREATED)

        return Response({'error': "Only Teachers can add data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, format=None):
        if request.user.usertype == 'teacher':
            try:
                enrolled = Attendance.objects.filter(id=request.data['id'])
            except:
                return Response({'error': "Enrollment Id Not Found!"}, status=status.HTTP_404_NOT_FOUND)

            if enrolled:
                enrolled.delete()

                return Response({'msg': 'Enrollment deleted successfully!'}, status=status.HTTP_200_OK)

            return Response({'error': 'Enrollment Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only students can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserInstructorsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        if request.user.usertype in ['admin', 'teacher']:
            if request.user.usertype == 'admin':
                courseid = request.GET.get('courseid')
                # assigned = (Instructors.objects.filter(courseid=courseid).values_list('teacherid', flat=True))
                # teachers = User.objects.filter(usertype='teacher').exclude(id__in=list(Instructors.objects.filter(courseid=courseid).values_list('teacherid', flat=True)))
                assigned = Instructors.objects.filter(courseid=courseid)
                rem = list(assigned.values_list('teacherid', flat=True))
                teachers = User.objects.filter(
                    usertype='teacher').exclude(id__in=rem)

                serializerT = UserProfileSerializer(
                    data=teachers, many=True)
                serializerA = UserInstructorsSerializer(
                    data=assigned, many=True)

                serializerT.is_valid()
                serializerA.is_valid()

                return Response({"assigned": list(serializerA.data), "unassigned": list(serializerT.data)},
                                status=status.HTTP_200_OK)
            if request.user.usertype == 'teacher':
                assigned = Instructors.objects.filter(
                    teacherid=request.user.id)
                serializer = UserInstructorsSerializer(
                    data=assigned, many=True)
                serializer.is_valid()
                return Response({"assigned": list(serializer.data)},
                                status=status.HTTP_200_OK)

        if request.user.usertype == 'student':
            courses = Instructors.objects.all()
            serializer = UserInstructorsSerializer(courses, many=True)

            return Response({"enrolls": serializer.data},
                            status=status.HTTP_200_OK)

        return Response({'error': "You are not authorized!"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        if request.user.usertype == 'admin':
            serializer = UserInstructorsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"msg": "Course Assigned to Teacher."}, status=status.HTTP_201_CREATED)
        return Response({'error': "Only Admins can add and delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, format=None):
        if request.user.usertype == 'admin':
            try:
                enrolled = Instructors.objects.filter(
                    teacherid=request.data['teacherid'], courseid=request.data['courseid'])
            except:
                return Response({'error': "Course Assignment Not Found!"}, status=status.HTTP_404_NOT_FOUND)

            if enrolled:
                enrolled.delete()

                return Response({'msg': 'Course Assignment deleted successfully!'}, status=status.HTTP_200_OK)

            return Response({'error': 'Course Assignment Not Found!'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogOut(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        logout(request)

        return Response({'msg': 'User Logged out Successfully!'}, status=status.HTTP_200_OK)
