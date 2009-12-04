from django.conf.urls.defaults import *

from views import add_view_for

urlpatterns = patterns('',
    url(r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', add_view_for, name="popularity-add-view-for"),
)