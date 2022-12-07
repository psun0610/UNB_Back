from django.db import models

# Create your models here.


class profile(models.Model):
    grade = models.IntegerField(default=0)
