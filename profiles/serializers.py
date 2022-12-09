from rest_framework import serializers
from .models import *


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ("pk", "name", "image")


class UserBadgeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = [
            "pk",
            "user",
            "badge",
        ]


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ("user", "total", "today")


class ProfileSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = Profiles
        fields = ("grade", "badge")
