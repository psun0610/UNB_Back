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
