# Generated by Django 2.2.10 on 2020-04-04 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20200402_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpostcomment',
            name='blog_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.BlogPost'),
        ),
    ]