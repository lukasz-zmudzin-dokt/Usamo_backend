# Generated by Django 2.2.10 on 2020-04-22 21:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0003_cv_was_reviewed'),
    ]

    operations = [
        migrations.AddField(
            model_name='cv',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
