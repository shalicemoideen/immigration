# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=100)),
                ('requested_date', models.DateTimeField(auto_now_add=True)),
                ('reported_date', models.DateTimeField(null=True, blank=True)),
                ('token', models.CharField(max_length=200)),
                ('status', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Employee',
            },
        ),
        migrations.CreateModel(
            name='EmployeeDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('required', models.BooleanField(default=False)),
                ('file', models.FileField(upload_to=b'documents/')),
                ('status', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Employee-document',
            },
        ),
        migrations.AlterModelOptions(
            name='document',
            options={'verbose_name': 'Document'},
        ),
        migrations.RemoveField(
            model_name='document',
            name='email',
        ),
        migrations.RemoveField(
            model_name='document',
            name='employee_id',
        ),
        migrations.RemoveField(
            model_name='document',
            name='identity_proof',
        ),
        migrations.RemoveField(
            model_name='document',
            name='passport',
        ),
        migrations.RemoveField(
            model_name='document',
            name='passport_expiry',
        ),
        migrations.RemoveField(
            model_name='document',
            name='password_hash',
        ),
        migrations.RemoveField(
            model_name='document',
            name='reported_date',
        ),
        migrations.RemoveField(
            model_name='document',
            name='requested_date',
        ),
        migrations.RemoveField(
            model_name='document',
            name='status',
        ),
        migrations.RemoveField(
            model_name='document',
            name='visa',
        ),
        migrations.AddField(
            model_name='document',
            name='name',
            field=models.CharField(default=datetime.datetime(2017, 4, 25, 6, 31, 47, 638069, tzinfo=utc), max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employeedocument',
            name='document',
            field=models.ForeignKey(to='core.Document'),
        ),
        migrations.AddField(
            model_name='employeedocument',
            name='employee',
            field=models.ForeignKey(to='core.Employee'),
        ),
    ]
