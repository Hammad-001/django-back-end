# path
from django.urls import path

# views
from api.views import SendEmailToUserForPasswordRestView, UserChangePasswordView, UserLogOut, \
    UserLoginView, UserPasswordResetView, UserProfileView, UserView, UserCourseView, UserEnrollView,\
         UserInstructorsView, UserAttendanceView

# from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # For Users View
    path('users/', UserView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogOut.as_view(), name='logout'),
    # path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('password-reset/', SendEmailToUserForPasswordRestView.as_view(),
         name='passwordrestemail'),
    path('password-reset/<uid>/<token>/',
         UserPasswordResetView.as_view(), name='passwordrest'),

    # For Users View
    path('courses/', UserCourseView.as_view(), name='userCourses'),
    path('enrolled/', UserEnrollView.as_view(), name='enroll'),
    path('attendance/', UserAttendanceView.as_view(), name='attendance'),
    path('instructors/', UserInstructorsView.as_view(), name='instructors'),
]
