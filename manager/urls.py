from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^applications$', 'manager.views.applications', name='applications'),
                       url(r'^repositories$', 'manager.views.repositories', name='repositories'),

                       url(r'^admin/', include(admin.site.urls)),
)
