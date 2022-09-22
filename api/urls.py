# path
from django.urls import path

# views
from api.views.CourseView import UserCourseView
from api.views.EnrollmentView import UserEnrollView
from api.views.AttendanceView import UserAttendanceView
from api.views.InstructorsView import UserInstructorsView
from api.views.UserView import UserView, UserLoginView, UserProfileView, UserChangePasswordView,\
    UserPasswordResetView, SendEmailToUserForPasswordRestView, UserProfileView, UserLogOut

urlpatterns = [
    path('users/', UserView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogOut.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('password-reset/', SendEmailToUserForPasswordRestView.as_view(),
         name='passwordrestemail'),
    path('password-reset/<uid>/<token>/',
         UserPasswordResetView.as_view(), name='passwordrest'),
    path('courses/', UserCourseView.as_view(), name='userCourses'),
    path('enrolled/', UserEnrollView.as_view(), name='enroll'),
    path('attendance/', UserAttendanceView.as_view(), name='attendance'),
    path('instructors/', UserInstructorsView.as_view(), name='instructors'),
]
