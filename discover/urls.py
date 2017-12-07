from django.conf.urls import url

from . import views

app_name = 'discover'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<trip_id>[0-9]+)/detail/$', views.detail, name='detail'),
    url(r'^join/$', views.join, name='join'),
    url(r'^leave/$', views.leave, name='leave'),
    url(r'^organize/$', views.organize, name='organize'),
    url(r'^createTrip/$', views.createTrip, name='createTrip'),
    url(r'^taxilist/$', views.taxiList, name='taxiList'),
    url(r'^enroute/$', views.enroute, name='enroute'),
    url(r'^refresh/$', views.refreshtrips, name='refresh'),
    url(r'^back/$', views.back, name='back'),
]
