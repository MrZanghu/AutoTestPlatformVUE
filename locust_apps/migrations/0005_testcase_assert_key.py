# Generated by Django 3.2 on 2024-04-23 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locust_apps', '0004_auto_20240419_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcase',
            name='assert_key',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='断言内容'),
        ),
    ]