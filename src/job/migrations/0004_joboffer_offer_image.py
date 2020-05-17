# Generated by Django 2.2.10 on 2020-05-16 18:27

from django.db import migrations, models
import job.utils


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0003_joboffer_confirmed'),
    ]

    operations = [
        migrations.AddField(
            model_name='joboffer',
            name='offer_image',
            field=models.ImageField(null=True, upload_to=job.utils.create_job_offer_image_path),
        ),
    ]