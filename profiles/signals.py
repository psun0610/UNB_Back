from accounts.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profiles, Score


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profiles.objects.create(user=instance)


@receiver(post_save, sender=Score)
def check_score(sender, instance, **kwargs):
    user = instance.user
    user_score = Score.objects.get(user=user)
    user_profile = Profiles.objects.get(user=user)
    if user_score.total >= 300:
        user_profile.grade = 2
    elif user_score.total >= 600:
        user_profile.grade = 3
    elif user_score.total >= 1000:
        user_profile.grade = 4
    elif user_score.total >= 1600:
        user_profile.grade = 5
    elif user_score.total >= 2500:
        user_profile.grade = 6
    user_profile.save()
