# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0005_applicationbuild_build_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Cloning repository'), (3, b'Repository cloned'), (-1, b'Failed to create application'), (-2, b'Unknown')]),
            preserve_default=True,
        ),
    ]
