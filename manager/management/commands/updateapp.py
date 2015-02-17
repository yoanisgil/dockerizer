__author__ = 'Yoanis Gil'

from django.core.management.base import BaseCommand, CommandError
from manager.models import Application
from optparse import make_option
import os
import git


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
                repository = application.repository

                branch = repository.default_branch

                if 'branch' in options:
                    branch = options['branch']

                if not os.path.exists(repository.destination):
                    raise CommandError('Application %s has not been bootstrapped' % repository.location)

                repo = git.Repo(repository.destination)

                origin = repo.remote('origin')
                repo.create_head(branch, origin.refs[branch]).set_tracking_branch(origin.refs[branch])
                origin.pull()
            except Application.DoesNotExist:
                raise CommandError('Application "%s" does not exist' % application_name)


