# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_employee_division'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeedocument',
            name='received_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
