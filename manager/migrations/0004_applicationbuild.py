# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_auto_20150217_0321'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationBuild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_id', models.TextField()),
                ('tag', models.CharField(max_length=255)),
                ('branch', models.CharField(max_length=255)),
                ('commit', models.CharField(max_length=255)),
                ('application', models.ForeignKey(to='manager.Application')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
