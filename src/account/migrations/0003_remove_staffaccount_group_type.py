# Generated by Django 2.2.10 on 2020-04-23 20:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20200404_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffaccount',
            name='group_type',
        ),
    ]
