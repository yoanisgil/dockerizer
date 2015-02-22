__author__ = 'Yoanis Gil'

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from manager.docker_manager import DockerManager
from manager.models import Application


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--application', action='store', dest='application', help='Application name'),
        make_option('--branch', action='store', dest='branch', help='Branch to update'))

    help = 'Update application repository (or clone if not already required)'

    def handle(self, *args, **options):
        if 'application' in options:
            application_name = options['application']

            try:
                application = Application.objects.get(name=application_name)

                branch = application.repository.default_branch

                if 'branch' in options:
                    branch = options['branch']

                docker_manager = DockerManager()

                application_build = docker_manager.build_application(application, branch)

                self.stdout.write("Built image with id %s" % application_build.image_id)
                self.stdout.write("Image tag: %s" % application_build.tag)
            except Application.DoesNotExist:
                raise CommandError('Application "%s" does not exist' % application_name)

