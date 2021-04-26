from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    unique_id = models.IntegerField(blank=True, null=True)
    random_field = models.CharField(max_length=40, blank=True, null=True)