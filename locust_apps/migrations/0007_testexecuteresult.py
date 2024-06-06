# Generated by Django 3.2 on 2024-06-03 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locust_apps', '0006_auto_20240522_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestExecuteResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('belong_test_execute', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.IntegerField(blank=True, help_text='0：表示未执行，1：表示已执行', null=True)),
                ('type', models.IntegerField(blank=True, help_text='0：表示用例，1：表示集合', null=True)),
                ('case_suite_list', models.CharField(blank=True, max_length=1024, null=True, verbose_name='用例/集合id列表')),
                ('ex_u', models.IntegerField(blank=True, null=True)),
                ('ex_r', models.IntegerField(blank=True, null=True)),
                ('ex_t', models.IntegerField(blank=True, null=True)),
                ('creator', models.CharField(blank=True, max_length=50, null=True)),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '压力执行结果记录表',
                'verbose_name_plural': '压力执行结果记录表',
                'db_table': 'loc_test_execute_result',
            },
        ),
    ]