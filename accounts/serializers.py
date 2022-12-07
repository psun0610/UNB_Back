from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from .models import User
from dj_rest_auth.serializers import UserDetailsSerializer
from articles.serializers import *


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            "nickname",
            "badge",
        )


class CustomUserRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField()

    def get_cleaned_data(self):
        super(CustomUserRegisterSerializer, self).get_cleaned_data()
        return {
            "email": self.validated_data.get("email", ""),
            "nickname": self.validated_data.get("nickname", ""),
            "password1": self.validated_data.get("password1", ""),
            "password2": self.validated_data.get("password2", ""),
        }

    def save(self, request):
        user = super().save(request)
        user.nickname = self.data.get("nickname")
        user.save()
        return user


class UserInfo(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer(read_only=True)
    article = serializers.SerializerMethodField()
    user_pick = serializers.SerializerMethodField()

    def get_article(self, obj):
        article = list(obj.article_set.all())
        return InfoArticleSerializer(article, many=True).data

    def get_user_pick(self, obj):
        user_pick = list(obj.pick_set.all())
        return PickSerializer(user_pick, many=True).data

    class Meta:
        model = User
        fields = ["user", "nickname", "article", "user_pick", "badge"]
