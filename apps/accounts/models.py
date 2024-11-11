from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timedelta

class CustomUser(AbstractUser):
    failed_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
