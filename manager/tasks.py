from __future__ import absolute_import

from celery import shared_task

from .docker_manager import DockerManager
from .models import Application


@shared_task
def create_application(user_id, application_name, application_template, repository_url, repository_type):
    DockerManager.create_application(user_id, application_name, application_template, repository_url, repository_type)

@shared_task
def build_application(application_id, branch, user_id):
    manager = DockerManager()
    application = Application.objects.get(pk=application_id)
    manager.build_application(application, branch, user_id)