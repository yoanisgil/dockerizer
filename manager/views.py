from django.template import RequestContext

__author__ = 'Yoanis Gil'

from django.shortcuts import render_to_response


def home(request):
    return render_to_response('index.html', {},  context_instance=RequestContext(request))
