__author__ = 'Yoanis Gil'

from django.contrib.auth.models import User
from django.db import models


class Repository(models.Model):
    url = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    default_branch = models.CharField(max_length=255, default='master')

    def __unicode__(self):
        return self.url


class Application(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    repository = models.OneToOneField(Repository)
    template = models.CharField(max_length=255, default='django-1.7')

    def __unicode__(self):
        return self.name


class ApplicationBuild(models.Model):
    application = models.ForeignKey(Application)
    image_id = models.TextField()
    tag = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    commit = models.CharField(max_length=255)
    built_by = models.ForeignKey(User)
    launched_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True)

    def __unicode__(self):
        return "%s/%s:%s" % (self.built_by, self.application.name, self.tag)


class BuildLogEntry(models.Model):
    application_build = models.ForeignKey(ApplicationBuild)
    entry_content = models.TextField()
    generated_at = models.DateField(auto_now_add=True)

    @staticmethod
    def record_new_entry(*args, **kwargs):
        entry = BuildLogEntry(*args, **kwargs)
        entry.save()

        return entry

    def __unicode__(self):
        return "%s:%s" % (self.generated_at, self.entry_content)


