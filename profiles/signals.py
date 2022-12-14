from accounts.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *
import datetime
import calendar

today = datetime.date.today()
year = today.year
month = today.month
day = today.day
monthrange = calendar.monthrange(year, month)[1]


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
    if user_score.today != 0:
        try:
            grass = Grass.objects.get(
                user=user, year=year, month=month, monthrange=monthrange
            )
            if day not in grass.daylist:
                grass.daylist.append(day)
            grass.save()

            daylist = grass.daylist
            if len(grass.daylist) == 1:
                consecutive = 1
            else:
                cnt = 1
                daymax1 = []
                daymax2 = []
                for i in daylist:
                    daymax1.append(i)
                daymax1.append(0)
                for i in range(len(daylist)):
                    if daymax1[i + 1] - daymax1[i] == 1:
                        cnt += 1
                    else:
                        daymax2.append(cnt)

                        cnt = 1
                print(daymax2)
                consecutive = max(daymax2)
            grass.consecutive = consecutive
            grass.save()
        except:
            pass

    def get_badge(grade, user):
        badge = Badge.objects.get(pk=grade)
        try:
            UserBadge.objects.get(user=user, badge=badge)
        except:
            UserBadge.objects.create(user=user, badge=badge)

    def best_badge(grade, user):
        badge = Badge.objects.get(pk=8)
        try:
            UserBadge.objects.get(user=user, badge=badge)
        except:
            UserBadge.objects.create(user=user, badge=badge)

    if user_score.total >= 2500:
        user_profile.grade = 7
        get_badge(7, user)
    elif user_score.total >= 1600:
        user_profile.grade = 6
        get_badge(6, user)
    elif user_score.total >= 1000:
        user_profile.grade = 5
        get_badge(5, user)
    elif user_score.total >= 600:
        user_profile.grade = 4
        get_badge(4, user)
    elif user_score.total >= 300:
        user_profile.grade = 3
        get_badge(3, user)
    elif user_score.total >= 30:
        user_profile.grade = 2
        get_badge(2, user)

    user_profile.save()
    all_today = Score.objects.filter(updated=today).order_by("-today").first()
    today_user = TodayUser.objects.filter(created_at=today)
    if len(today_user) == 0:
        TodayUser.objects.create(user=user)
        print("베스트유저생성")
        # 이때 뱃지 지급
        yet_user = TodayUser.objects.get(
            created_at=datetime.datetime.now() - datetime.timedelta(days=1)
        )
        best_badge(8, yet_user.user)
        print("베스트유저 뱃지 지급")
    else:
        best_user = today_user.first()
        best_user.user = all_today.user
        best_user.save()
        print("베스트유저변경")
