from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^applications$', 'manager.views.applications', name='applications'),
                       url(r'^application/builds/(?P<application_id>\d+)$', 'manager.views.application_builds',
                           name='application-builds'),
                       url(r'^application/builds/launch/(?P<build_id>\d+)$', 'manager.views.launch_build',
                           name='launch-build'),
                       url(r'^application/builds/stop/(?P<build_id>\d+)$', 'manager.views.stop_build',
                           name='stop-build'),
                       url(r'^admin/', include(admin.site.urls)),
)
