from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from profiles.serializers import *
from .models import User
from dj_rest_auth.serializers import UserDetailsSerializer
from articles.serializers import *
from profiles.models import *


class BadgeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = "__all__"


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ("id","nickname",)


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
    profiles = serializers.SerializerMethodField()
    user_badges = UserBadgeSerializer(read_only=True, many=True)
    grade_percent = serializers.SerializerMethodField()

    def get_article(self, obj):
        article = list(obj.article_set.all())
        return InfoArticleSerializer(article, many=True, read_only=True).data

    def get_user_pick(self, obj):
        user_pick = list(obj.pick_set.all())
        return PickSerializer(user_pick, many=True, read_only=True).data

    def get_profiles(self, obj):
        profiles = obj.profiles.get(user=obj)
        return ProfileSerializer(profiles, read_only=True).data

    def get_grade_percent(self, obj):
        score = Score.objects.get(user=obj).total
        grade = Profiles.objects.get(user=obj).grade
        exp_percent = 0
        if grade == 1:
            exp_percent = (score / 30) * 100
        elif grade == 2:
            exp_percent = ((score - 30) / 300) * 100
        elif grade == 3:
            exp_percent = ((score - 300) / 300) * 100
        elif grade == 4:
            exp_percent = ((score - 600) / 400) * 100
        elif grade == 5:
            exp_percent = ((score - 1000) / 600) * 100
        elif grade == 6:
            exp_percent = ((score - 1600) / 900) * 100
        else:
            exp_percent = score
        print(round(exp_percent, 1))
        print(grade)
        return {round(exp_percent, 1)}

    class Meta:
        model = User
        fields = [
            "user",
            "nickname",
            "article",
            "user_pick",
            "profiles",
            "user_badges",
            "grade_percent",
        ]
