import uuid
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.utils import timezone
from django.utils.translation import pgettext_lazy


class UserManager(BaseUserManager):
    def create_user(
            self, email, password=None, is_staff=False, is_active=True,
            **extra_fields):
        """Create a user instance with the given email and password."""
        email = UserManager.normalize_email(email)
        user = self.model(
            email=email, is_active=is_active, is_staff=is_staff,
            **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(
            email, password, is_staff=True, is_superuser=True, **extra_fields)


def get_token():
    return str(uuid.uuid4())


class User(PermissionsMixin, AbstractBaseUser):
    language = models.CharField(max_length=50, blank=True, default='all')
    first_name = models.CharField(pgettext_lazy("User", "First name"), max_length=256, blank=True)
    last_name = models.CharField(pgettext_lazy("User", "Last name"), max_length=256, blank=True)
    email = models.EmailField(pgettext_lazy("User", "E-mail"), unique=True)
    email_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    news_subscribe = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        return self.first_name.title() + ' ' + self.last_name.title()

    def get_short_name(self):
        return self.first_name.title() + ' ' + self.last_name.title()