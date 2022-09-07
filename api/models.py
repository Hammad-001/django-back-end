from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class Course(models.Model):
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=100)


class UserManager(BaseUserManager):
    def create_user(self, email, usertype, first_name, last_name=None, cnic=None,  password=None):
        """
        Creates and saves a User with the given email, first_name, last_name, cnic, usertype, and password.
        """
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
        """
        Creates and saves a superUser with the given email, first_name, last_name, cnic, usertype, and password.
        """
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


class User(AbstractBaseUser, PermissionsMixin):
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
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin


class Enrolled(models.Model):
    courseid = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="courseEnrolled")
    studentid = models.ForeignKey(User, on_delete=models.CASCADE,related_name="studentEnrolled")
    result = models.IntegerField(null=True,blank=True)
    year = models.DateField(auto_now_add=True)



class Attendance(models.Model):
    studentid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="studentAttendance")
    courseid = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="courseAttendance")
    isabsent = models.BooleanField(default=True)
    date = models.DateField()


class Instructors(models.Model):
    courseid = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="courseInstructor")
    teacherid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacherInstructor")


