__author__ = 'Yoanis Gil'

from django.contrib import admin
from models import Repository, Application, ApplicationBuild, BuildLogEntry

@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass


@admin.register(ApplicationBuild)
class ApplicationBuildAdmin(admin.ModelAdmin):
    pass


@admin.register(BuildLogEntry)
class BuildLogEntryAdmin(admin.ModelAdmin):
    pass