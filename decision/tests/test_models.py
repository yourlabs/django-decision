from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model

from decision.models import Vote, Poll
from decision.exceptions import CantVoteAfterEndDate, ChoiceMustExist


class PollTestCase(TestCase):
    def setUp(self):
        for i in range(1, 6):
            if getattr(self, 'user%s' % i, False):
                continue

            setattr(self, 'user%s' % i, 
                    get_user_model().objects.create(
                    username='user%s' % i, 
                    email='user%s@example.com' % i))

    def test_cant_cheat_balance(self):
        fixture = Poll.objects.create(vote_end=date(2432, 5, 28))
        try:
            fixture.votes.create(user=self.user1, choice=3)
        except ChoiceMustExist:
            pass
        else:
            self.fail('Should not be able to have choice=3')

    def test_can_vote_before_end_date(self):
        fixture = Poll.objects.create(vote_end=date(2432, 5, 28))
        fixture.votes.create(user=self.user1, choice=Vote.AGREE)

    def test_cant_vote_after_end_date(self):
        fixture = Poll.objects.create(vote_end=date(1871, 5, 28))

        try:
            fixture.votes.create(user=self.user1, choice=Vote.AGREE)
        except CantVoteAfterEndDate:
            pass
        else:
            self.fail('Should not be able to vote after end date')

    def test_set_vote(self):
        def expect_votes(*votes):
            self.assertEquals(list(votes), [(vote.user, vote.choice) 
                for vote in fixture.votes.all()])

        fixture = Poll.objects.create(vote_end=date(2432, 5, 28))

        fixture.set_vote(self.user1, Vote.AGREE)
        expect_votes((self.user1, Vote.AGREE))

        fixture.set_vote(self.user2, Vote.AGREE)
        expect_votes((self.user1, Vote.AGREE), (self.user2, Vote.AGREE))

        fixture.set_vote(self.user1, Vote.AGAINST)
        expect_votes((self.user1, Vote.AGAINST), (self.user2, Vote.AGREE))

    def test_get_balance(self):
        fixture = Poll.objects.create(vote_end=date(2432, 5, 28))
        self.assertEquals(fixture.get_balance(), 0)

        fixture.set_vote(self.user1, Vote.AGAINST)
        self.assertEquals(fixture.get_balance(), -1)

        fixture.set_vote(self.user2, Vote.AGAINST)
        self.assertEquals(fixture.get_balance(), -2)

        fixture.set_vote(self.user3, Vote.AGREE)
        self.assertEquals(fixture.get_balance(), -1)

        fixture.set_vote(self.user4, Vote.AGREE)
        self.assertEquals(fixture.get_balance(), 0)

        fixture.set_vote(self.user5, Vote.AGREE)
        self.assertEquals(fixture.get_balance(), 1)
