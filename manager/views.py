__author__ = 'Yoanis Gil'

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from docker_manager import DockerManager, BuildAlreadyRunningException, BuildNotRunningException
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

    try:
        manager = DockerManager()
        manager.launch_build(build, ports_config={80: 8080})

        messages.add_message(request, messages.INFO, "{0} {1}". format(_("Launched build"), build))
    except BuildAlreadyRunningException, e:
        messages.add_message(request, messages.ERROR, e.message)

    return redirect('application-builds', application_id=build.application_id)


@login_required
def stop_build(request, build_id):
    try:
        build = get_object_or_404(ApplicationBuild, pk=build_id)

        manager = DockerManager()
        manager.stop_build(build)

        messages.add_message(request, messages.INFO, "{0} {1}". format(_("Stopped build"), build))
    except BuildNotRunningException, e:
        messages.add_message(request, messages.ERROR, e.message)

    return redirect('application-builds', application_id=build.application_id)


@login_required
def destroy_build(request, build_id):
    pass


@login_required
def repositories(request):
    return render_to_response('manager/repositories.html', {}, context_instance=RequestContext(request))
