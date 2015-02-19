from django.views import generic
from django import shortcuts
from django import http
from django.core.cache import cache

from .models import Poll, Vote


class PollVoteView(generic.DetailView):
    model = Poll

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise Exception()

        self.object = self.get_object()

        self.object.set_vote(request.user, int(kwargs['choice']))

        return shortcuts.render(request, 'decision/_poll_vote.html',
            {'object': self.object})
