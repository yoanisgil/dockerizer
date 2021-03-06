from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^$', 'manager.views.applications', name='index'),
                       url(r'^applications$', 'manager.views.applications', name='applications'),
                       url(r'^application/builds/(?P<application_id>\d+)$', 'manager.views.application_builds',
                           name='application-builds'),
                       url(r'^application/builds/launch/(?P<build_id>\d+)$', 'manager.views.launch_build',
                           name='launch-build'),
                       url(r'^application/builds/stop/(?P<build_id>\d+)$', 'manager.views.stop_build',
                           name='stop-build'),
                       url(r'^application/builds/destroy/(?P<build_id>\d+)$', 'manager.views.destroy_build',
                           name='destroy-build'),
                       url(r'^application/destroy/(?P<application_id>\d+)$', 'manager.views.destroy_application',
                           name='destroy-application'),
                       url(r'^application/builds/image_logs/(?P<build_id>\d+)/after/(?P<after>\d+)',
                           'manager.views.build_image_logs',
                           name='build-image-logs'),
                       url(r'^application/builds/logs/(?P<build_id>\d+)$', 'manager.views.build_logs',
                           name='build-logs'),
                       url(r'^application/new$', 'manager.views.new_application',
                           name='new-application'),
                       url(r'^application/builds/(?P<application_id>\d+)/new$', 'manager.views.new_application_build',
                           name='new-application-build'),
                       # Registration urls
                       (r'^accounts/', include('registration.backends.default.urls')),
                       url(r'^admin/', include(admin.site.urls)),
)
