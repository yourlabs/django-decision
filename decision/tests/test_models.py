from datetime import date

from django import test
from django.contrib.auth import get_user_model

from decision.models import Category, Poll, Choice, Vote, Delegation
from decision.exceptions import *


User = get_user_model()


class TestCase(test.TestCase):
    def assertChoiceIs(self, user, choice):
        self.assertEquals(self.poll.get_user_choice(user), choice)

    def setUp(self):
        if getattr(self, 'ready', False):
            return

        self.category = Category.objects.create(name='test category')

        self.poll = self.create_poll(self.__class__.__name__)

        self.agree = self.poll.choices.create(name='Agree')
        self.disagree = self.poll.choices.create(name='Disagree')

        self.bottom = get_user_model().objects.create(username='bottom')
        self.middle = get_user_model().objects.create(username='middle')
        self.top = get_user_model().objects.create(username='top')

        # Bottom trusts middle for all
        self.bottom_middle = Delegation.objects.create(follower=self.bottom,
                leader=self.middle)

        # Middle trusts top on category
        self.middle_top = Delegation.objects.create(follower=self.middle,
                leader=self.top)

        self.ready = True

    def tearDown(self):
        Vote.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        Poll.objects.all().delete()
        Delegation.objects.all().delete()
        Category.objects.all().delete()


class BasicTests(object):
    def test_propagation_cant_override_my_vote(self):
        self.poll.set_vote(self.bottom, self.agree)
        self.poll.set_vote(self.middle, self.disagree)

        self.assertChoiceIs(self.bottom, self.agree)
        self.assertChoiceIs(self.middle, self.disagree)

    def test_propagation_defaults_my_vote(self):
        self.poll.set_vote(self.middle, self.agree)

        self.assertChoiceIs(self.bottom, self.agree)
        self.assertChoiceIs(self.middle, self.agree)

    def test_override_propagated_vote_myself(self):
        self.poll.set_vote(self.middle, self.disagree)
        self.poll.set_vote(self.bottom, self.agree)

        self.assertChoiceIs(self.middle, self.disagree)
        self.assertChoiceIs(self.bottom, self.agree)


class PollTestCase(BasicTests, TestCase):
    def create_poll(self, name):
        return Poll.objects.create(name=name)

    def test_propagation_does_NOT_cascade_because_of_category(self):
        """ 
        Delegation has a category, poll does not, propagation should not
        happen.
        """
        if self.category not in self.middle_top.categories.all():
            self.middle_top.categories.add(self.category)

        self.poll.set_vote(self.top, self.agree)
        
        self.assertChoiceIs(self.top, self.agree)
        self.assertChoiceIs(self.middle, None)
        self.assertChoiceIs(self.bottom, None)

    def test_propagation_cascades_on_category_free_delegations(self):
        """
        Delegation has no category, poll neither, propagation should work.
        """
        if self.category in self.middle_top.categories.all():
            self.middle_top.categories.remove(self.category)

        self.poll.set_vote(self.top, self.agree)
        
        self.assertChoiceIs(self.top, self.agree)
        self.assertChoiceIs(self.middle, self.agree)
        self.assertChoiceIs(self.bottom, self.agree)


class CategorisedPollTestCase(BasicTests, TestCase):
    def setUp(self):
        if getattr(self, 'ready', False):
            self.middle_top.categories.add(self.category)
        
        super(CategorisedPollTestCase, self).setUp()

    def create_poll(self, name):
        return Poll.objects.create(name=name, category=self.category)

    def test_propagation_cascade(self):
        self.poll.set_vote(self.top, self.agree)
        
        self.assertEquals(self.poll.get_user_choice(self.top), 
                self.agree)
        self.assertEquals(self.poll.get_user_choice(self.middle),
                self.agree)
        self.assertEquals(self.poll.get_user_choice(self.bottom),
                self.agree)

    def test_propagation_does_cascade_with_category(self):
        if self.category not in self.middle_top.categories.all():
            self.middle_top.categories.add(self.category)

        self.poll.set_vote(self.top, self.agree)
        
        self.assertChoiceIs(self.top, self.agree)
        self.assertChoiceIs(self.middle, self.agree)
        self.assertChoiceIs(self.bottom, self.agree)
