from __future__ import absolute_import

from celery import shared_task

from .docker_manager import DockerManager
from .models import Application, ApplicationBuild


@shared_task
def create_application(user_id, application_name, application_template, repository_url, repository_type):
    DockerManager.create_application(user_id, application_name, application_template, repository_url, repository_type)

@shared_task
def build_application(application_id, branch, user_id):
    application = Application.objects.get(pk=application_id)

    manager = DockerManager()
    manager.build_application(application, branch, user_id)

@shared_task
def destroy_application_build(application_build_id):
    application_build = ApplicationBuild.objects.get(pk=application_build_id)

    manager = DockerManager()
    manager.destroy_build(application_build)

@shared_task
def destroy_application(application_id):
    application = Application.objects.get(pk=application_id)

    manager = DockerManager()
    manager.destroy_application(application)