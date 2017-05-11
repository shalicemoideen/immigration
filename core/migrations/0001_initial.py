# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=70)),
                ('employee_id', models.IntegerField(null=True, blank=True)),
                ('visa', models.CharField(max_length=200, blank=True)),
                ('passport', models.CharField(max_length=200, blank=True)),
                ('identity_proof', models.CharField(max_length=200, blank=True)),
                ('passport_expiry', models.DateField(null=True, blank=True)),
                ('requested_date', models.DateTimeField(auto_now_add=True)),
                ('reported_date', models.DateTimeField(null=True, blank=True)),
                ('password_hash', models.CharField(max_length=200)),
                ('status', models.IntegerField(default=0)),
            ],
        ),
    ]
