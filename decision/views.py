from django.views import generic
from django import shortcuts
from django import http
from django.core.cache import cache

from rest_framework import viewsets

from .models import Poll, Category, Vote, Choice, Delegation
from .serializers import (PollSerializer, CategorySerializer,
        VoteSerializer, ChoiceSerializer, DelegationSerializer)


class PollVoteView(generic.DetailView):
    model = Poll

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise Exception()

        self.object = self.get_object()

        self.object.set_vote(request.user, int(kwargs['choice']))

        return shortcuts.render(request, 'decision/_poll_vote.html',
            {'object': self.object})


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class DelegationViewSet(viewsets.ModelViewSet):
    queryset = Delegation.objects.all()
    serializer_class = DelegationSerializer
