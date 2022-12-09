from django.db import models
from accounts.models import *
from django.conf import settings
from django_mysql.models import ListCharField

# Create your models here.
class Grass(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=models.CASCADE
    )
    year = models.IntegerField(blank=True)
    month = models.IntegerField(blank=True)
    monthrange = models.IntegerField(blank=True)
    daylist = ListCharField(
        base_field=models.IntegerField(blank=True), max_length=(30 * 30)
    )
    consecutive = models.IntegerField(blank=True, default=0)


class Badge(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to="badges")


class UserBadge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="user_badges",
    )
    badge = models.ForeignKey(Badge, null=False, blank=False, on_delete=models.CASCADE)


class Profiles(models.Model):
    grade = models.IntegerField(default=1)
    badge = models.ForeignKey(
        Badge, null=False, blank=False, on_delete=models.CASCADE, default=1
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="profiles",
    )


# 총점수, 일일 점수
class Score(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    # 토탈 스코어 = 유저의 픽 개수 * 10 + 유저의 게시글 * 20 + 유저의 댓글 * 5
    total = models.IntegerField(default=0)

    # 투데이 스코어 = 픽을 만들때마다 * 10 + 게시글 만들때마다 * 20 + 댓글 작성시마다 * 5
    today = models.IntegerField(default=0)

    updated = models.DateField(auto_now=True)


class TodayUser(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
