# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170515_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='subject',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
