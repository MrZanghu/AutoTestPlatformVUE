# Generated by Django 3.2 on 2023-09-08 17:30

from django.db import migrations, models
import main_platform.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_platform', '0007_alter_testsuite_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadscasetemplate',
            name='address',
            field=models.FileField(blank=True, null=True, upload_to=main_platform.models.uploads_file),
        ),
    ]
