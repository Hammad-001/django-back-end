from django.contrib import admin
from api.models import Attendance, Course, Enrolled, User, Instructors

# This file registers the models to show in them default django admin page


@admin.register(User)
# User Model Register
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name',
                    'last_name', 'cnic', 'usertype', 'is_active', 'is_admin']


@admin.register(Course)
# Course Model Register
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name']


@admin.register(Enrolled)
# Enrolled Model Register
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'courseid', 'studentid', 'result', 'year']


@admin.register(Attendance)
# Enrollment Model Register
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'courseid', 'studentid', 'date', 'isabsent']


@admin.register(Instructors)
# Instructors Model Register
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'courseid', 'teacherid', 'year']
