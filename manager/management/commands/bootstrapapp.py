__author__ = 'Yoanis Gil'

from django.core.management.base import BaseCommand, CommandError
from manager.models import Application
from optparse import make_option
import os
import git


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--application', action='store', dest='application', help='Application name'),)
    help = 'Update application repository (or clone if not already required)'

    def handle(self, *args, **options):
        if 'application' in options:
            application_name = options['application']

            try:
                application = Application.objects.get(name=application_name)
                repository = application.repository

                if os.path.exists(repository.destination):
                    raise CommandError('Application %s already bootstrapped' % repository.destination)

                git.Repo.clone_from(repository.url, repository.destination, branch=repository.default_branch)
            except Application.DoesNotExist:
                raise CommandError('Application "%s" does not exist' % application_name)
