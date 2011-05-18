from django.conf.urls.defaults import *
from bugtracker.issues.views import *
urlpatterns = patterns('issues.views',
    (r'^$', index),
    (r'^my/$', my_issues),
    (r'^lookups/$', lookups),
    (r'^lookups/create/$', lookups_create),
    (r'^lookups/delete/$', lookups_delete),
    (r'^create/$', issue_create),
    (r'^search/$', search),
    (r'^details/(?P<id>\d+)/$', issue_details),
    (r'^issue/(?P<id>\d+)/update/$', issue_update)
)
