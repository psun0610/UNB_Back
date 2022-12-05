# models.py
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers


class UserManager(BaseUserManager):
    def create_user(self, email, password, nickname, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=email,
            nickname=nickname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, nickname, **extra_fields):
        superuser = self.create_user(
            email=email,
            password=password,
            nickname=nickname,
        )
        superuser.is_staff = True
        superuser.is_admin = True
        superuser.is_active = True
        superuser.is_superuser = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    nickname = models.CharField(max_length=20, null=False, blank=False, default="")
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    badge = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["nickname"]

    def __str__(self):
        return self.nickname


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
