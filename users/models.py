# users/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio        = models.TextField(blank=True)
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)
    reputation = models.IntegerField(default=0)
    location   = models.CharField(max_length=100, blank=True)
    website    = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"