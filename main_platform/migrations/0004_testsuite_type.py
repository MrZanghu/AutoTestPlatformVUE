# Generated by Django 3.2 on 2023-07-26 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_platform', '0003_delete_testcaseforsea'),
    ]

    operations = [
        migrations.AddField(
            model_name='testsuite',
            name='type',
            field=models.CharField(blank=True, choices=[(1, 'UI'), (2, 'API')], max_length=128, null=True, verbose_name='用例集合类型'),
        ),
    ]
