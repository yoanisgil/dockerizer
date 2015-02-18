# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manager', '0004_applicationbuild'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildLogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entry_content', models.TextField()),
                ('generated_at', models.DateField(auto_now_add=True)),
                ('application_build', models.ForeignKey(to='manager.ApplicationBuild')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='application',
            name='owner',
        ),
        migrations.AddField(
            model_name='applicationbuild',
            name='built_by',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicationbuild',
            name='finished_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 18, 1, 36, 54, 515801, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicationbuild',
            name='launched_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 18, 1, 37, 0, 688799, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
