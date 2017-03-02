"""Sieve urls."""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^savefs/(?P<name>.+)/$', views.savefs, name="fs_save"),
    url(r'^newfs/$', views.new_filters_set, name="fs_add"),
    url(r'^removefs/(?P<name>.+)/$', views.remove_filters_set,
        name="fs_delete"),
    url(r'^activatefs/(?P<name>.+)/$', views.activate_filters_set,
        name="fs_activate"),
    url(r'^downloadfs/(?P<name>.+)/$', views.download_filters_set,
        name="fs_download"),
    url(r'^templates/(?P<ftype>\w+)/$', views.get_templates,
        name="templates_get"),
    url(r'^(?P<setname>.+)/newfilter/$', views.newfilter,
        name="filter_add"),
    url(r'^(?P<setname>.+)/editfilter/(?P<fname>.+)/$', views.editfilter,
        name="filter_change"),
    url(r'^(?P<setname>.+)/removefilter/(?P<fname>.+)/$', views.removefilter,
        name="filter_delete"),
    url(r'^(?P<setname>.+)/togglestate/(?P<fname>.+)/$',
        views.toggle_filter_state, name="filter_toggle_state"),
    url(r'^(?P<setname>.+)/moveup/(?P<fname>.+)/$',
        views.move_filter_up, name="filter_move_up"),
    url(r'^(?P<setname>.+)/movedown/(?P<fname>.+)/$',
        views.move_filter_down, name="filter_move_down"),
    url(r'^(?P<name>.+)/$', views.getfs, name="fs_get"),
]
