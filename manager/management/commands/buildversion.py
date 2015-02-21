__author__ = 'Yoanis Gil'

from django.contrib.auth.models import User
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from manager.models import Application, ApplicationBuild, BuildLogEntry
from optparse import make_option
from django.conf import settings

import re
import os
import git
import ssl
import json
import docker
import shutil
import tempfile


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
                    raise CommandError('Application %s has not been bootstrapped' % repository.destination)

                repo = git.Repo(repository.destination)

                if repo.is_dirty():
                    raise CommandError('Repository %s is dirty' % repository.destination)

                repo.heads[branch].checkout()

                build_dir = os.path.join(settings.BASE_DIR, 'docker_templates', application.template.name)

                tmp_dir = tempfile.mkdtemp(suffix='dockerizer')
                dst_dir = os.path.join(tmp_dir, 'build')
                shutil.copytree(build_dir, dst_dir)

                os.link(repository.destination, os.path.join(dst_dir, 'app'))

                if not settings.DOCKER_TLS_VERIFY:
                    tls_config = False
                else:
                    cert_path = settings.DOCKER_CERT_PATH
                    if cert_path:
                        ca_cert_path = os.path.join(cert_path, 'ca.pem')
                        client_cert = (
                            os.path.join(cert_path, 'cert.pem'),
                            os.path.join(cert_path, 'key.pem')
                        )

                    tls_config = docker.tls.TLSConfig(
                        ssl_version=ssl.PROTOCOL_TLSv1,
                        client_cert=client_cert,
                        verify=ca_cert_path,
                        assert_hostname=False
                    )

                cli = docker.Client(base_url=settings.DOCKER_HOST, tls=tls_config)

                image_id = None

                builder = User.objects.get(username='admin')
                tag = repo.head.commit.name_rev[0:12]
                image_repository = "%s/%s" % (builder.username, application_name)

                application_build = ApplicationBuild()
                application_build.application = application
                application_build.branch = branch
                application_build.commit = repo.head.commit.name_rev
                application_build.built_by = builder
                application_build.launched_at = timezone.now()

                application_build.save()

                for line in cli.build(rm=True, path=dst_dir):
                    data = json.loads(line)

                    if 'stream' in data:
                        search = r'Successfully built ([0-9a-f]+)'
                        match = re.search(search, data['stream'])
                        if match:
                            image_id = match.group(1)

                    entry = BuildLogEntry.record_new_entry(application_build=application_build, entry_content=line)
                    print entry

                self.stdout.write("Built image with id %s" % image_id)

                tagged = cli.tag(image=image_id, tag=tag, repository=image_repository)

                if tagged:
                    self.stdout.write("Image tag: %s" % tag)
                    self.stdout.write("Image repository: %s" % image_repository)

                os.unlink(os.path.join(dst_dir, 'app'))
                shutil.rmtree(tmp_dir)

                application_build.image_id = image_id
                application_build.tag = tag
                application_build.finished_at = timezone.now()

                application_build.save()
            except Application.DoesNotExist:
                raise CommandError('Application "%s" does not exist' % application_name)

