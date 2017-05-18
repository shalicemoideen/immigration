# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20170425_0631'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='employeedocument',
            name='file',
            field=models.FileField(null=True, upload_to=b'documents/', blank=True),
        ),
    ]
