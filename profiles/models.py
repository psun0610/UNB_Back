from django.db import models
from django.conf import settings

# Create your models here.


class Badge(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to="badges")


class UserBadge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="user_badge",
    )
    badge = models.ForeignKey(Badge, null=False, blank=False, on_delete=models.CASCADE)


class UsingBadge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="using_badge",
    )
    badge = models.ForeignKey(
        Badge, null=False, blank=False, on_delete=models.CASCADE, default=1
    )

class profile(models.Model):
    grade = models.IntegerField(default=0)

