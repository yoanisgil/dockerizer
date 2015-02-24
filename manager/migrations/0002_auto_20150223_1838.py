# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='buildlogentry',
            options={'verbose_name_plural': 'Build Log Entries'},
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={'verbose_name_plural': 'repositories'},
        ),
        migrations.AddField(
            model_name='repository',
            name='repository_type',
            field=models.IntegerField(default=1, choices=[(1, b'Git'), (2, b'Mercurial')]),
            preserve_default=True,
        ),
    ]
