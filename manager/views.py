from django.core.urlresolvers import reverse

__author__ = 'Yoanis Gil'

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect

from docker_manager import DockerManager, BuildAlreadyRunningException, BuildNotRunningException
from models import Application, ApplicationBuild, BuildLogEntry
from forms import NewApplicationForm, NewApplicationBuildForm
from tasks import build_application as task_build_application, create_application as task_create_application, \
    destroy_application as task_destroy_application

import datetime


@login_required
def applications(request):
    apps = Application.objects.filter(owner=request.user)

    return render_to_response('manager/applications.html', {'applications': apps},
                              context_instance=RequestContext(request))


@login_required
def new_application(request):
    if request.method == 'POST':
        form = NewApplicationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            task_create_application.apply_async((
                request.user.id, cleaned_data['application_name'], cleaned_data['application_template'],
                cleaned_data['repository_url'], cleaned_data['repository_type']))

            messages.add_message(request, messages.INFO,
                                 "{0}".format(_("Application created, bootstrap is in progress ")))

            return redirect('applications')

    else:
        form = NewApplicationForm()

    return render_to_response('manager/new_application.html', {'form': form},
                              context_instance=RequestContext(request))


@login_required
def application_builds(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    builds = ApplicationBuild.objects.filter(application_id=application_id).order_by('-finished_at')

    return render_to_response('manager/application_builds.html', {'application': application, 'builds': builds},
                              context_instance=RequestContext(request))


@login_required
def new_application_build(request, application_id):
    response = {'status': 0, 'message': ''}

    application = get_object_or_404(Application, pk=application_id)

    if request.method == 'POST':
        form = NewApplicationBuildForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            branch = cleaned_data['branch']

            application_build = ApplicationBuild()
            application_build.application = application
            application_build.branch = branch
            application_build.built_by = request.user

            application_build.save()
            task_build_application.apply_async((application_build.id, cleaned_data['branch']))
            #task_build_application(application_build.id, cleaned_data['branch'])

            response['message'] = "{0} {1}".format(_("Created application build for "), application.name)
            response['build_image_logs_url'] = reverse('build-image-logs',
                                                       args=(
                                                           application_build.id,
                                                           datetime.datetime.now().strftime('%s')))
            return JsonResponse(response)
        else:
            response['status'] = 1
            response['message'] = 'Invalid form data'
    else:
        form = NewApplicationBuildForm()

    return render_to_response('manager/new_application_build.html', {'form': form, 'application_id': application_id},
                              context_instance=RequestContext(request))


@login_required
def launch_build(request, build_id):
    build = get_object_or_404(ApplicationBuild, pk=build_id)

    try:
        manager = DockerManager()
        manager.launch_build(build, ports_config={80: 8080})

        messages.add_message(request, messages.INFO, "{0} {1}".format(_("Launched build"), build))
    except BuildAlreadyRunningException, e:
        messages.add_message(request, messages.ERROR, e.message)

    return redirect('application-builds', application_id=build.application_id)


@login_required
def stop_build(request, build_id):
    try:
        application_build = get_object_or_404(ApplicationBuild, pk=build_id)

        manager = DockerManager()
        manager.stop_build(application_build)

        messages.add_message(request, messages.INFO, "{0} {1}".format(_("Stopped build"), application_build))
    except BuildNotRunningException, e:
        messages.add_message(request, messages.ERROR, e.message)

    return redirect('application-builds', application_id=application_build.application_id)


@login_required
def destroy_build(request, build_id):
    application_build = get_object_or_404(ApplicationBuild, pk=build_id)

    manager = DockerManager()
    manager.destroy_build(application_build)

    return redirect('application-builds', application_id=application_build.application_id)


@login_required
def build_logs(request, build_id):
    application_build = get_object_or_404(ApplicationBuild, pk=build_id)

    manager = DockerManager()
    logs = manager.build_logs(application_build)

    return render_to_response('manager/build_logs.html', {'logs': logs, 'application_build': application_build},
                              context_instance=RequestContext(request))


@login_required
def build_image_logs(request, build_id, after):
    application_build = get_object_or_404(ApplicationBuild, pk=build_id)

    response = {'status': application_build.build_status}

    if not application_build.build_success() and not application_build.build_failed():
        response['status'] = 0
        after_datetime = datetime.datetime.fromtimestamp(float(after))

        entries = BuildLogEntry.objects.filter(application_build=application_build,
                                               generated_at__gte=after_datetime).order_by('-generated_at')

        data = []

        for entry in entries:
            data.append({'entry_content': entry.entry_content, 'generated_at': entry.generated_at})

        response['build_image_logs_url'] = reverse('build-image-logs',
                                                   args=(
                                                       build_id, datetime.datetime.now().strftime('%s')))
        response['data'] = data

    return JsonResponse(response)


@login_required
def destroy_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    task_destroy_application.apply_async((application_id,))

    messages.add_message(request, messages.INFO,
                         "{0} {1}".format(_("Destroying application "), application.name))

    return redirect('applications')


@login_required
def repositories(request):
    return render_to_response('manager/repositories.html', {}, context_instance=RequestContext(request))
