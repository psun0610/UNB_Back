from rest_framework import serializers
from .models import *
from profiles.models import Score


class BadgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Badge
        fields = "__all__"


class UserBadgeSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")
    badge = BadgeSerializer(many=True, read_only=True)

    class Meta:
        model = UserBadge
        fields = [
            "pk",
            "user",
            "badge",
        ]


class UsingBadgeSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UsingBadge
        fields = [
            "pk",
            "user",
            "badge",
        ]


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ("user", "total")
