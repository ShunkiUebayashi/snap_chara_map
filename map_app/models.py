# map_app/models.py

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Theme(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ["name", "theme"]

    def __str__(self):
        return self.name


class Photo(models.Model):
    image = models.ImageField(upload_to="photos/")
    caption = models.CharField(max_length=200, blank=True)
    taken_at = models.DateTimeField()
    uploaded_at = models.DateTimeField(default=timezone.now)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo at {self.location.name}"
