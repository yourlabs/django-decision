from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register('poll', views.PollViewSet)
router.register('category', views.CategoryViewSet)
router.register('vote', views.VoteViewSet)
router.register('choice', views.ChoiceViewSet)
router.register('delegation', views.DelegationViewSet)


urlpatterns = [
    url(
        r'(?P<pk>\d+)/vote/(?P<choice>-?\d)/$',
        views.PollVoteView.as_view(),
        name='decision_poll_vote',
    ),
    url(r'^', include(router.urls)),
]
