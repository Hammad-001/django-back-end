# Generated by Django 4.1 on 2022-09-22 05:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=255, unique=True, verbose_name="email address"
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=200, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=200, verbose_name="last name"),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_admin", models.BooleanField(default=False)),
                ("cnic", models.CharField(max_length=15, unique=True)),
                ("usertype", models.CharField(max_length=7)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("isabsent", models.BooleanField(default=True)),
                ("date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=8)),
                ("name", models.CharField(max_length=100)),
                (
                    "attendance",
                    models.ManyToManyField(
                        related_name="attendance",
                        through="api.Attendance",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Instructors",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("year", models.DateField(auto_now_add=True)),
                (
                    "courseid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="courseInstructors",
                        to="api.course",
                    ),
                ),
                (
                    "teacherid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Instructor",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Enrolled",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("result", models.IntegerField(blank=True, null=True)),
                ("year", models.DateField(auto_now_add=True)),
                (
                    "courseid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="courseEnrolled",
                        to="api.course",
                    ),
                ),
                (
                    "studentid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="studentEnrolled",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="course",
            name="enrolled",
            field=models.ManyToManyField(
                related_name="enrolled",
                through="api.Enrolled",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="instructors",
            field=models.ManyToManyField(
                related_name="instructors",
                through="api.Instructors",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="attendance",
            name="courseid",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="courseAttendance",
                to="api.course",
            ),
        ),
        migrations.AddField(
            model_name="attendance",
            name="studentid",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="studentAttendance",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
