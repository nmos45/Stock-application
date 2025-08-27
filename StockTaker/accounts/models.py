from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Model representing a User Profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.CharField(max_length=400, blank=True, null=True)
