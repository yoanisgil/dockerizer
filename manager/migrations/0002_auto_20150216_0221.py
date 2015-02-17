# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='template',
            field=models.CharField(default=b'django-1.7', max_length=255),
            preserve_default=True,
        ),
    ]
