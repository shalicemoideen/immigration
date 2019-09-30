# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20170524_0813'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('email', models.EmailField(max_length=100)),
            ],
            options={
                'verbose_name': 'Customer type',
                'verbose_name_plural': 'Customer type',
            },
        ),
        migrations.AddField(
            model_name='employee',
            name='description',
            field=models.TextField(max_length=4000, null=True, blank=True),
        ),
    ]
