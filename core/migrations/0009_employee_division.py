# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20170529_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='division',
            field=models.ForeignKey(default=1, to='core.Division'),
            preserve_default=False,
        ),
    ]
