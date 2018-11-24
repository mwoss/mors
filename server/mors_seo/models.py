from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=30)

    def __str__(self):
        return f'User: {self.username}, email: {self.email}'
