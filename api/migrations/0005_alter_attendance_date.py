# Generated by Django 4.1 on 2022-08-30 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_alter_enrolled_result"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attendance",
            name="date",
            field=models.DateField(),
        ),
    ]
