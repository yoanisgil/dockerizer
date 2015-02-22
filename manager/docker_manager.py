__author__ = 'Yoanis Gil'

from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from manager.models import ApplicationBuild, BuildLogEntry

import re
import os
import git
import ssl
import json
import docker
import shutil
import tempfile


class ApplicationNotBuildException(Exception):
    pass


class DirtyRepositoryException(Exception):
    pass


class BuildAlreadyRunningException(Exception):
    pass


class BuildNotRunningException(Exception):
    pass


class DockerCliFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_client():
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

        return docker.Client(base_url=settings.DOCKER_HOST, tls=tls_config)


class DockerManager:
    def __init__(self):
        self.client = DockerCliFactory.get_client()

    def build_application(self, application, branch):
        repository = application.repository

        if not os.path.exists(repository.destination):
            raise ApplicationNotBuildException('Application %s has not been bootstrapped' % repository.destination)

        repo = git.Repo(repository.destination)

        if repo.is_dirty():
            raise DirtyRepositoryException('Repository %s is dirty' % repository.destination)

        repo.heads[branch].checkout()

        build_dir = os.path.join(settings.BASE_DIR, 'docker_templates', application.template.name)

        tmp_dir = tempfile.mkdtemp(suffix='dockerizer')
        dst_dir = os.path.join(tmp_dir, 'build')
        shutil.copytree(build_dir, dst_dir)

        os.link(repository.destination, os.path.join(dst_dir, 'app'))

        image_id = None

        builder = User.objects.get(username='admin')
        tag = repo.head.commit.name_rev[0:12]
        image_repository = "%s/%s" % (builder.username, application.name)

        application_build = ApplicationBuild()
        application_build.application = application
        application_build.branch = branch
        application_build.commit = repo.head.commit.name_rev
        application_build.built_by = builder
        application_build.launched_at = timezone.now()

        application_build.save()

        for line in self.build(rm=True, path=dst_dir):
            data = json.loads(line)

            if 'stream' in data:
                search = r'Successfully built ([0-9a-f]+)'
                match = re.search(search, data['stream'])
                if match:
                    image_id = match.group(1)

            BuildLogEntry.record_new_entry(application_build=application_build, entry_content=line)

        self.client.tag(image=image_id, tag=tag, repository=image_repository)

        os.unlink(os.path.join(dst_dir, 'app'))
        shutil.rmtree(tmp_dir)

        application_build.image_id = image_id
        application_build.tag = tag
        application_build.finished_at = timezone.now()

        application_build.save()

        return application_build

    def build_is_running(self, application_build):
        containers = self.get_containers_for_application_build(application_build)

        return len(containers) > 0 and containers[0]['Status'].lower().startswith("up")

    def build_is_stopped(self, application_build):
        return not self.build_is_running(application_build)

    def get_containers_for_application_build(self, application_build):
        containers = self.client.containers(all=True)
        image_name = "%s/%s:%s" % (
            application_build.built_by.username, application_build.application.name, application_build.tag)
        result = []

        for container in containers:

            if container['Image'] == image_name:
                result.append(container)

        return containers

    def launch_build(self, application_build, ports_config={}):
        containers = self.get_containers_for_application_build(application_build)

        if len(containers) == 0:
            application = application_build.application
            command = application.template.launch_command

            container_id = self.client.create_container(image=application_build.image_id, command=command, detach=True,
                                                        tty=False,
                                                        ports=ports_config.keys())

            self.client.start(container_id, port_bindings=ports_config)

            return container_id
        elif not self.build_is_running(application_build):
            self.client.start(containers[0]['Id'], port_bindings=ports_config)
        else:
            raise BuildAlreadyRunningException("Build %s is already running" % application_build)

    def stop_build(self, application_build):
        if self.build_is_running(application_build):
            containers = self.get_containers_for_application_build(application_build)

            self.client.stop(containers[0])
        else:
            raise BuildNotRunningException("Build %s is not running" % application_build)
