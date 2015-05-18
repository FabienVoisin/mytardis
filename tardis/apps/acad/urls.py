from django.conf.urls import patterns, include, url
from tardis.apps.acad import views

urlpatterns = patterns('',
    url(r'^source/$', views.source_index),
    url(r'^source/(?P<id>\w+)/$', views.source_detail),
    url(r'^search/$', views.search_source, name='search_source'),
)
