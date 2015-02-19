from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(
        r'(?P<pk>\d+)/vote/(?P<choice>-?\d)/$',
        views.PollVoteView.as_view(),
        name='decision_poll_vote',
    ),
)
