# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manager', '0002_auto_20150216_0221'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='owner',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application',
            name='repository',
            field=models.OneToOneField(to='manager.Repository'),
            preserve_default=True,
        ),
    ]
