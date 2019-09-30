# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20170529_0652'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CustomerType',
            new_name='Division',
        ),
        migrations.AlterModelOptions(
            name='division',
            options={'verbose_name': 'Division', 'verbose_name_plural': 'Division'},
        ),
    ]
