# Generated by Django 3.2 on 2023-07-27 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_platform', '0006_alter_testsuite_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testsuite',
            name='type',
            field=models.IntegerField(blank=True, choices=[(1, 'UI'), (0, 'API')], null=True, verbose_name='用例集合类型'),
        ),
    ]
