# Generated by Django 2.2.10 on 2020-04-27 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joboffer',
            name='company_address',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.Address'),
        ),
    ]
