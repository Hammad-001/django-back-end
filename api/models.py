from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    # User Model's Manager

    def create_user(self, email, usertype, first_name, last_name=None, cnic=None,  password=None):
        """Creates and saves a User with the given email, first_name, last_name, cnic, usertype, and password."""

        # if there is no email, password or first name in provided object
        # it doesnot let admin add that user

        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            raise ValueError('Users must have an password')

        if not first_name:
            raise ValueError('Users must have an first name')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            cnic=cnic,
            usertype=usertype,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, usertype, first_name, last_name=None, cnic=None,  password=None):
        """Creates and saves a superUser with the given email, first_name, last_name, cnic, usertype, and password."""

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            cnic=cnic,
            usertype=usertype,
        )

        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    # Users Model

    email = models.EmailField(
        verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(verbose_name='first name', max_length=200)
    last_name = models.CharField(verbose_name='last name', max_length=200)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    cnic = models.CharField(max_length=15, unique=True)
    usertype = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name',
                       'cnic', 'usertype']

    def __str__(self):
        return self.first_name + " " + self.last_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_active

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_active


class Course(models.Model):
    # Course Modelmodels

    code = models.CharField(max_length=8)
    name = models.CharField(max_length=100)

    # Many-to-Many fields
    instructors = models.ManyToManyField(
        User, through='Instructors', related_name='instructors')
    enrolled = models.ManyToManyField(
        User, through='Enrolled', related_name='enrolled')
    attendance = models.ManyToManyField(
        User, through='Attendance', related_name='attendance')


class Enrolled(models.Model):
    # Student Enrollment Model

    # One-to-Many Fields
    courseid = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='courseEnrolled')
    studentid = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='studentEnrolled')

    # Other Fields
    result = models.IntegerField(null=True, blank=True)
    year = models.DateField(auto_now_add=True)


class Attendance(models.Model):
    # Student Attendance Model

    # One-to-Many Fields
    courseid = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='courseAttendance')
    studentid = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='studentAttendance')

    # Other Fields
    isabsent = models.BooleanField(default=True)
    date = models.DateField()


class Instructors(models.Model):
    # Course Instructors Model

    # One-to-Many Fields
    courseid = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='courseInstructors')
    teacherid = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='Instructor')

    # Other Fields
    year = models.DateField(auto_now_add=True)
