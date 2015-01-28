from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^sample/', include('sample.urls')),
)
