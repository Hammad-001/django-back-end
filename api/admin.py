from django.contrib import admin

from api.models import Attendance, Course, Enrolled, User, Instructors


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name',
                    'last_name', 'cnic', 'usertype', 'is_admin', 'is_active']


@admin.register(Course)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name']


@admin.register(Enrolled)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'courseid', 'studentid', 'result', 'year']


@admin.register(Attendance)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'studentid', 'courseid', 'date', 'isabsent']


@admin.register(Instructors)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'courseid', 'teacherid']
