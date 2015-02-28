__author__ = 'Yoanis Gil'

from django.contrib.auth.models import User
from django.db import models


class Repository(models.Model):
    GIT = 1
    MERCURIAL = 2

    TYPES = (
        (GIT, 'Git'),
        (MERCURIAL, 'Mercurial')
    )

    class Meta:
        verbose_name_plural = "repositories"

    url = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    default_branch = models.CharField(max_length=255, default='master')
    repository_type = models.IntegerField(choices=TYPES, default=GIT)

    def __unicode__(self):
        return self.url


class ApplicationTemplate(models.Model):
    name = models.CharField(max_length=255)
    launch_command = models.TextField()

    def __unicode__(self):
        return self.name


class Application(models.Model):
    CREATED = 1
    CLONING_REPO = 2
    REPO_CLONED = 3
    FAILED_TO_CREATE = -1
    UNKNOWN = -2

    STATUS = ((CREATED, 'Created'),
              (CLONING_REPO, 'Cloning repository'),
              (REPO_CLONED, 'Repository cloned'),
              (FAILED_TO_CREATE, 'Failed to create application'),
              (UNKNOWN, 'Unknown'))

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    repository = models.OneToOneField(Repository)
    template = models.ForeignKey(ApplicationTemplate)
    status = models.IntegerField(choices=STATUS, default=CREATED)

    def __unicode__(self):
        return self.name

    def status_description(self):
        for status in Application.STATUS:
            status_id, description = status

            if self.status == status_id:
                return description


class ApplicationBuild(models.Model):
    CREATED = 1
    BUILDING = 2
    FAILED = 3
    BUILT = 4

    STATUS = ((CREATED, 'Created'), (BUILDING, 'Building'), (FAILED, 'Failed'), (BUILT, 'Built'))

    application = models.ForeignKey(Application)
    image_id = models.TextField()
    tag = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    commit = models.CharField(max_length=255, null=True)
    built_by = models.ForeignKey(User)
    launched_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    build_status = models.IntegerField(choices=STATUS, default=CREATED)

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

    def build_has_container(self):
        return len(self._manager.get_containers_for_application_build(self)) > 0

    def is_building(self):
        return self.build_status == ApplicationBuild.BUILDING

    def build_success(self):
        return self.build_status == ApplicationBuild.BUILT

    def build_failed(self):
        return self.build_status == ApplicationBuild.FAILED


class BuildLogEntry(models.Model):
    class Meta:
        verbose_name_plural = "Build Log Entries"

    application_build = models.ForeignKey(ApplicationBuild)
    entry_content = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def record_new_entry(*args, **kwargs):
        entry = BuildLogEntry(*args, **kwargs)
        entry.save()

        return entry

    def __unicode__(self):
        return "%s:%s" % (self.generated_at, self.entry_content)