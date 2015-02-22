__author__ = 'Yoanis Gil'

from django.contrib.auth.models import User
from django.db import models


class Repository(models.Model):
    class Meta:
        verbose_name_plural = "repositories"

    url = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    default_branch = models.CharField(max_length=255, default='master')

    def __unicode__(self):
        return self.url


class ApplicationTemplate(models.Model):
    name = models.CharField(max_length=255)
    launch_command = models.TextField()

    def __unicode__(self):
        return "%s: %s" % (self.name, self.launch_command)


class Application(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    repository = models.OneToOneField(Repository)
    template = models.ForeignKey(ApplicationTemplate)

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

    def __init__(self, *args, **kwargs):
        from docker_manager import DockerManager

        super(ApplicationBuild, self).__init__(*args, **kwargs)
        self._manager = DockerManager()

    def __unicode__(self):
        return "%s/%s:%s" % (self.built_by, self.application.name, self.tag)

    def is_running(self):
        return self._manager.build_is_running(self)

    def is_stopped(self):
        return not self.is_running

    def status_description(self):
        containers = self._manager.get_containers_for_application_build(self)

        description = ''

        if len(containers) > 0:
            description = containers[0]['Status']

        return description


class BuildLogEntry(models.Model):
    class Meta:
        verbose_name_plural = "Build Log Entries"

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