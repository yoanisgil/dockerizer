# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicationBuild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_id', models.TextField()),
                ('tag', models.CharField(max_length=255)),
                ('branch', models.CharField(max_length=255)),
                ('commit', models.CharField(max_length=255)),
                ('launched_at', models.DateTimeField()),
                ('finished_at', models.DateTimeField(null=True)),
                ('application', models.ForeignKey(to='manager.Application')),
                ('built_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicationTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('launch_command', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255)),
                ('destination', models.CharField(max_length=255)),
                ('default_branch', models.CharField(default=b'master', max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='application',
            name='repository',
            field=models.OneToOneField(to='manager.Repository'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='template',
            field=models.ForeignKey(to='manager.ApplicationTemplate'),
            preserve_default=True,
        ),
    ]
