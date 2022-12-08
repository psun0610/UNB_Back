from accounts.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *
import datetime
import calendar

today = datetime.date.today()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # print("create", created)
    # print(instance)
    today = datetime.date.today()
    year = today.year
    month = today.month
    monthrange = calendar.monthrange(year, month)[1]
    if created:
        Profiles.objects.create(user=instance)
        UserBadge.objects.create(user=instance, badge=Badge.objects.get(pk=1))
        Score.objects.create(user=instance)
        Grass.objects.create(
            user=instance, year=year, month=month, monthrange=monthrange
        )
        # print("프로필 생성완료")


@receiver(post_save, sender=Score)
def check_score(sender, instance, **kwargs):
    user = instance.user
    user_score = Score.objects.get(user=user)
    user_profile = Profiles.objects.get(user=user)

    def get_badge(grade):
        badge = Badge.objects.get(pk=grade)
        try:
            UserBadge.objects.get(user=user, badge=badge)
        except:
            UserBadge.objects.create(user=user, badge=badge)

    if user_score.total >= 30:
        user_profile.grade = 2
        get_badge(2)
    elif user_score.total >= 300:
        user_profile.grade = 3
        get_badge(3)
    elif user_score.total >= 600:
        user_profile.grade = 4
        get_badge(4)
    elif user_score.total >= 1000:
        user_profile.grade = 5
        # get_badge(5)
    elif user_score.total >= 1600:
        user_profile.grade = 6
        # get_badge(6)
    elif user_score.total >= 2500:
        user_profile.grade = 7
        # get_badge(7)
    user_profile.save()
    all_today = Score.objects.filter(updated=today).order_by("-today").first()
    todayuser = TodayUser.objects.filter(updated_at=today)
    if len(todayuser) == 0:
        TodayUser.objects.create(user=user)
        print("베스트유저생성")
    else:
        best_user = todayuser.first()
        best_user.user = all_today.user
        best_user.save()
        print("베스트유저변경")
