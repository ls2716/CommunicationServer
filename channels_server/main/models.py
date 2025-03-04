# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    api_key = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class Room(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    webhook = models.CharField(max_length=100, blank=True, null=True, default='')

    def __str__(self):
        return self.owner.username +"_"+self.name


class Endpoint(models.Model):
    code = models.CharField(max_length=100)
    permissions = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=None)
    identity = models.CharField(
        max_length=100
    )  # This is the identifiable information of the endpoint

    def __str__(self):
        return self.code
