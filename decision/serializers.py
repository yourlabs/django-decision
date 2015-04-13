from rest_framework import serializers

from .models import Poll, Category, Vote, Choice, Delegation


class PollSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Poll


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category


class VoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vote


class ChoiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Choice


class DelegationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Delegation
