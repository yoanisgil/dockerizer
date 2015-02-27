# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20150223_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buildlogentry',
            name='generated_at',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
