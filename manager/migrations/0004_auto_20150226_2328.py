# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_auto_20150226_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationbuild',
            name='commit',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationbuild',
            name='launched_at',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
