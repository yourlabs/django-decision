from datetime import date

from django.conf import settings
from django.utils.translation import ugettext as _
from django.db import models
from django.db.models import signals
from django.core.cache import cache

from .exceptions import CantVoteAfterEndDate, ChoiceMustExist


def get_poll_choice_cache_key(poll, choice):
    return 'decision:pc:%s:%s' % (poll.pk, choice)


def get_user_choice_cache_key(poll, user):
    return 'decision:uv:%s:%s' % (poll.pk, user.pk)


class Poll(models.Model):
    vote_end = models.DateField(null=True, blank=True)

    def set_vote(self, user, choice):
        try:
            vote = self.votes.get(user=user)
        except Vote.DoesNotExist:
            vote = self.votes.create(user=user, choice=choice)
        else:
            vote.choice = choice
            vote.save()

        cache.set(get_user_choice_cache_key(self, user), choice, None)

        choices = Vote.objects.all().distinct('choice').order_by('choice'
                ).values_list('choice', flat=True)

        for c in choices:
            cache.delete(get_poll_choice_cache_key(self, c))

        return vote

    def get_user_choice(self, user):
        key = get_user_choice_cache_key(self, user)
        value = cache.get(key)

        if value is None:
            try:
                vote = self.votes.get(user=user)
            except Vote.DoesNotExist:
                value = False
            else:
                value = str(vote.choice)

            cache.set(key, value, None)

        return value

    def get_balance(self):
        return self.votes.aggregate(models.Sum('choice'))['choice__sum'] or 0

    def get_vote_count(self, choice):
        key = get_poll_choice_cache_key(self, choice)
        value = cache.get(key)

        if value is None:
            value = self.votes.filter(choice=choice).count()
            cache.set(key, value)

        return value

    def get_agree_count(self):
        return self.get_vote_count(Vote.AGREE)

    def get_abstain_count(self):
        return self.get_vote_count(Vote.ABSTAIN)

    def get_against_count(self):
        return self.get_vote_count(Vote.AGAINST)


class Vote(models.Model):
    AGAINST = -1
    ABSTAIN = 0
    AGREE = 1

    CHOICES = (
        (AGREE, _(u'agree')),
        (ABSTAIN, _(u'abstain')),
        (AGAINST, _(u'against')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes')
    poll = models.ForeignKey('Poll', related_name='votes')
    choice = models.IntegerField(choices=CHOICES)

    class Meta:
        unique_together = ('user', 'poll')
        ordering = ('pk',)


def cant_vote_after_poll_vote_end(sender, instance, **kwargs):
    if instance.poll.vote_end is None:
        return

    if date.today() > instance.poll.vote_end:
        raise CantVoteAfterEndDate()
signals.pre_save.connect(cant_vote_after_poll_vote_end, sender=Vote)


def cant_cheat_balance(sender, instance, **kwargs):
    if instance.choice not in [c[0] for c in Vote.CHOICES]:
        raise ChoiceMustExist()
signals.pre_save.connect(cant_cheat_balance, sender=Vote)
