# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_auto_20150226_2328'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationbuild',
            name='build_status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Building'), (3, b'Failed'), (4, b'Built')]),
            preserve_default=True,
        ),
    ]
