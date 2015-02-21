from django.template import RequestContext

__author__ = 'Yoanis Gil'

from django.shortcuts import render_to_response


def applications(request):
    return render_to_response('manager/applications.html', {},  context_instance=RequestContext(request))


def repositories(request):
    return render_to_response('manager/repositories.html', {},  context_instance=RequestContext(request))
