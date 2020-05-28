# Generated by Django 2.2.10 on 2020-05-27 16:16

import cv.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CV',
            fields=[
                ('cv_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, null=True)),
                ('template', models.CharField(max_length=40)),
                ('is_verified', models.BooleanField(default=False)),
                ('was_reviewed', models.BooleanField(default=False)),
                ('has_picture', models.BooleanField(default=False)),
                ('document', models.FileField(upload_to='cv_docs/%Y/%m/%d/')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('cv_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_user', to='account.DefaultAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('cv_id', models.UUIDField(primary_key=True, serialize=False, validators=[cv.models.validate_cv_id])),
                ('basic_info', models.TextField(blank=True)),
                ('schools', models.TextField(blank=True)),
                ('experiences', models.TextField(blank=True)),
                ('skills', models.TextField(blank=True)),
                ('languages', models.TextField(blank=True)),
                ('additional_info', models.TextField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
                ('cv', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='cv.CV')),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('date_start', models.CharField(max_length=7)),
                ('date_end', models.CharField(max_length=7, null=True)),
                ('additional_info', models.CharField(max_length=150, null=True)),
                ('cv', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schools', to='cv.CV')),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('level', models.CharField(max_length=20)),
                ('cv', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='languages', to='cv.CV')),
            ],
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=400)),
                ('date_start', models.CharField(max_length=7)),
                ('date_end', models.CharField(max_length=7, null=True)),
                ('cv', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='cv.CV')),
            ],
        ),
        migrations.CreateModel(
            name='BasicInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('picture', models.ImageField(upload_to='cv_pics/%Y/%m/%d/')),
                ('phone_number', models.CharField(max_length=12)),
                ('date_of_birth', models.CharField(max_length=12)),
                ('cv', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='basic_info', to='cv.CV')),
            ],
        ),
    ]
