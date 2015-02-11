from datetime import date

from django.conf import settings
from django.utils.translation import ugettext as _
from django.db import models
from django.db.models import signals

from .exceptions import CantVoteAfterEndDate, ChoiceMustExist


class Proposal(models.Model):
    vote_end = models.DateField()

    def set_vote(self, user, choice):
        try:
            vote = self.votes.get(user=user)
        except Vote.DoesNotExist:
            return self.votes.create(user=user, choice=choice)

        vote.choice = choice
        vote.save()
        return vote

    def get_balance(self):
        return self.votes.aggregate(models.Sum('choice'))['choice__sum'] or 0


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
    proposal = models.ForeignKey('Proposal', related_name='votes')
    choice = models.IntegerField(choices=CHOICES)

    class Meta:
        unique_together = ('user', 'proposal')
        ordering = ('pk',)


def cant_vote_after_proposal_vote_end(sender, instance, **kwargs):
    if date.today() > instance.proposal.vote_end:
        raise CantVoteAfterEndDate()
signals.pre_save.connect(cant_vote_after_proposal_vote_end, sender=Vote)


def cant_cheat_balance(sender, instance, **kwargs):
    if instance.choice not in [c[0] for c in Vote.CHOICES]:
        raise ChoiceMustExist()
signals.pre_save.connect(cant_cheat_balance, sender=Vote)
