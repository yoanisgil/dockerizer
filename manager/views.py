__author__ = 'Yoanis Gil'

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from docker_manager import DockerManager
from models import Application, ApplicationBuild


@login_required
def applications(request):
    apps = Application.objects.filter(owner=request.user)

    return render_to_response('manager/applications.html', {'applications': apps},
                              context_instance=RequestContext(request))


@login_required
def application_builds(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    builds = ApplicationBuild.objects.filter(application=application).order_by('-finished_at')

    return render_to_response('manager/application_builds.html', {'': application, 'builds': builds},
                              context_instance=RequestContext(request))


@login_required
def launch_build(request, build_id):
    build = get_object_or_404(ApplicationBuild, pk=build_id)

    manager = DockerManager()
    manager.launch_application(build, ports_config={80: 8080})

    return redirect('application-builds', application_id=build.application_id)


@login_required
def stop_build(request, build_id):
    pass


@login_required
def destroy_build(request, build_id):
    pass


@login_required
def repositories(request):
    return render_to_response('manager/repositories.html', {}, context_instance=RequestContext(request))
