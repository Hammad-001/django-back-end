# Response and permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# for auth
from django.contrib.auth import authenticate, logout

# for rendering errors
from api.renderers import UserRenderer

# Models
from api.models import User

# serializers
from api.serializer.UserSerializer import UserRegistrationSerializer, UserProfileSerializer, \
    UserChangePasswordSerializer, SendEmailTOUserForPasswordResetSerializer, UserPasswordRestSerializer

# creating custom user auth token
from rest_framework_simplejwt.tokens import RefreshToken

# Tokens


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


Roles = {'Admin': 'admin', 'Teacher': 'teacher', 'Student': 'student'}


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        """This function return user on base of requested role based on request. It works only for admins."""
        if request.user.usertype == Roles['Admin']:
            usertype = request.GET.get('usertype')
            if usertype == None or usertype == 'All':
                users = User.objects.filter(is_active=True)
            else:
                users = User.objects.filter(usertype=usertype, is_active=True)
            userSerializer = UserRegistrationSerializer(users, many=True)
            return Response({'users': userSerializer.data}, status=status.HTTP_200_OK)
        return Response({'error': "Only admins can View Users!"}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        """This function creates a User with proper role. Only admins can create Users."""
        if request.user.usertype == Roles['Admin']:
            userSerializer = UserRegistrationSerializer(data=request.data)
            userSerializer.is_valid(raise_exception=True)
            return Response({"msg": "User is Registered."}, status=status.HTTP_201_CREATED)
        return Response({'error': "Only admins can create Users!"}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request):
        """This function creates a User with proper role. Only admins can create Users."""
        if request.user.usertype == Roles['Admin']:
            change = request.data['change']
            user = User.objects.get(
                email=request.data['email'], is_active=False)
            if change == True:
                user.is_active = True
                user.save(update_fields=['is_active'])
            elif change == False:
                user.delete()
                userSerializer = UserRegistrationSerializer(
                    data=request.data['data'])
                userSerializer.is_valid(raise_exception=True)
                return Response({"msg": "User is Registered."}, status=status.HTTP_201_CREATED)
            return Response({"msg": "User is Registered."}, status=status.HTTP_201_CREATED)
        return Response({'error': "Only admins can create Users!"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        """This function updates the provided User with provided data. Only admins can update Users."""
        if request.user.usertype == Roles['Admin']:
            user = User.objects.get(pk=request.data['id'])
            if user:
                user.cnic = request.data['cnic']
                user.email = request.data['email']
                user.usertype = request.data['usertype']
                user.last_name = request.data['last_name']
                user.first_name = request.data['first_name']
                user.save(update_fields=[
                          'first_name', 'last_name', 'usertype', 'email', 'cnic'])
                return Response({"msg": "User Updated successfully."}, status=status.HTTP_200_OK)
            return Response({'error': 'User Not Found!'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        """This function soft deletes the requested User. Only admins can update Users."""
        if request.user.usertype == Roles['Admin']:
            user = User.objects.get(id=request.data['id'])
            if user:
                user.is_active = False
                user.save(update_fields=['is_active'])
                return Response({'msg': 'User deleted successfully!'}, status=status.HTTP_200_OK)
            return Response({'error': 'Requested user Not Found!'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': "Only admins can add, edit or delete data!"}, status=status.HTTP_401_UNAUTHORIZED)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        """This function performs login functionality for all users."""
        email = request.data['email']
        password = request.data['password']
        user = authenticate(email=email, password=password, is_active=True)
        if user:
            token = get_tokens_for_user(user)
            return Response({"token": token['access'], "usertype": user.usertype, 'first_name': user.first_name}, status=status.HTTP_200_OK)
        return Response({'error': ['Email or Password is not valid!']}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """This function provides profile details for all users."""
        profileSerializer = UserProfileSerializer(request.user)
        return Response(profileSerializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """This function provides change password functionality for all users."""
        changePassSerializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user})
        changePassSerializer.is_valid(raise_exception=True)
        return Response({"msg": "password changed successfully!"}, status=status.HTTP_200_OK)


class SendEmailToUserForPasswordRestView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        """This function provides Reset password via email sending functionality for all users."""
        EmailSerializer = SendEmailTOUserForPasswordResetSerializer(
            data=request.data)
        EmailSerializer.is_valid(raise_exception=True)
        return Response({"msg": "Password Reset link sent to given Provided Email"}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token):
        """This function provides Reset password via email validation functionality for all users."""
        serializer = UserPasswordRestSerializer(
            data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({"msg": "password reset successfully."}, status=status.HTTP_200_OK)


class UserLogOut(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """This function logout the User.."""
        logout(request)
        return Response({'msg': 'User Logged out Successfully!'}, status=status.HTTP_200_OK)
