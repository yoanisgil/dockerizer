# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0005_auto_20150218_0137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationbuild',
            name='finished_at',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
