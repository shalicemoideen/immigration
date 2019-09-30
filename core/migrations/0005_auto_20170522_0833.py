# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_employee_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='email_copy',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='subject',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
