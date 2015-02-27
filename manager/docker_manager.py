__author__ = 'Yoanis Gil'

from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from manager.models import ApplicationBuild, BuildLogEntry, Application, Repository

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


class ContainerNotFoundException(Exception):
    pass


class BuildImageNotFoundException(Exception):
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

    @staticmethod
    def create_application(user_id, application_name, application_template, repository_url, repository_type):
        repository = Repository()
        repository.url = repository_url
        tmp_dir = tempfile.mkdtemp(suffix='dockerizer')
        repository.destination = os.path.join(tmp_dir, application_name)
        repository.repository_type = repository_type

        repository.save()

        user = User.objects.get(pk=user_id)
        application = Application()
        application.owner = user
        application.name = application_name
        application.repository = repository
        application.template = application_template

        git.Repo.clone_from(repository.url, repository.destination, branch=repository.default_branch)

        repository.save()
        application.save()

        return application

    def build_application(self, application_build, branch):
        try:
            application_build.status = ApplicationBuild.BUILDING

            application = application_build.application
            repository = application.repository

            if not os.path.exists(repository.destination):
                raise ApplicationNotBuildException('Application %s has not been bootstrapped' % repository.destination)

            repo = git.Repo(repository.destination)

            if repo.is_dirty():
                raise DirtyRepositoryException('Repository %s is dirty' % repository.destination)

            application_build.commit = repo.head.commit.name_rev
            application_build.launched_at = timezone.now()
            application_build.save()

            origin = repo.remote('origin')
            repo.create_head(branch, origin.refs[branch]).set_tracking_branch(origin.refs[branch])

            BuildLogEntry.record_new_entry(application_build=application_build,
                                           entry_content="Checking out branch {0}".format(branch))
            repo.heads[branch].checkout()

            BuildLogEntry.record_new_entry(application_build=application_build, entry_content="Pulling latest changes")
            origin.pull()

            build_dir = os.path.join(settings.BASE_DIR, 'docker_templates', application.template.name)

            tmp_dir = tempfile.mkdtemp(suffix='dockerizer')
            dst_dir = os.path.join(tmp_dir, 'build')
            shutil.copytree(build_dir, dst_dir)

            os.link(repository.destination, os.path.join(dst_dir, 'app'))

            image_id = None

            tag = repo.head.commit.name_rev[0:12]
            image_repository = "%s/%s" % (application_build.built_by.username, application.name)

            for line in self.client.build(rm=True, path=dst_dir):
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

            application_build.build_status = ApplicationBuild.BUILT

            application_build.save()
        except Exception, e:
            application_build.build_status = ApplicationBuild.FAILED
            application_build.save()

            raise e

    def get_containers_for_application_build(self, application_build):
        containers = self.client.containers(all=True)
        image_name = "%s/%s:%s" % (
            application_build.built_by.username, application_build.application.name, application_build.tag)
        result = []

        for container in containers:

            if container['Image'] == image_name:
                result.append(container)

        return result

    def get_container_for_application_build(self, application_build):
        containers = self.get_containers_for_application_build(application_build)

        if len(containers) == 0:
            raise ContainerNotFoundException("Cannot find container for build {0}".format(application_build))

        return containers[0]

    def build_is_running(self, application_build):
        containers = self.get_containers_for_application_build(application_build)

        return len(containers) > 0 and containers[0]['Status'].lower().startswith("up")

    def build_is_stopped(self, application_build):
        return not self.build_is_running(application_build)

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
            container = self.get_container_for_application_build(application_build)

            self.client.stop(container)
        else:
            raise BuildNotRunningException("Build %s is not running" % application_build)

    def build_logs(self, application_build, lines_count=100):
        container = self.get_container_for_application_build(application_build)

        logs = self.client.logs(container['Id'], tail=lines_count).split('\n')
        logs.reverse()

        return logs

    def image_for_build(self, application_build):
        images = self.client.images(all=True)

        images = [image for image in images if image['Id'].startswith(application_build.image_id)]

        if len(images) == 0:
            raise BuildImageNotFoundException("Cannot find image for build" % application_build)

        return images[0]

    def destroy_build(self, application_build):
        try:
            container = self.get_container_for_application_build(application_build)

            if self.build_is_running(application_build):
                self.stop_build(application_build)

            self.client.remove_container(container)
        except ContainerNotFoundException:
            pass

        build_image = self.image_for_build(application_build)

        self.client.remove_image(build_image)

        application_build.delete()

    def destroy_application(self, application):
        builds = ApplicationBuild.objects.filter(application=application)

        for build in builds:
            self.destroy_build(build)

        shutil.rmtree(application.repository.destination)

        application.repository.delete()
        application.delete()









