
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Topic(models.Model):
    creation_date = models.DateField(default=timezone.now)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return "Topic: " + str(self.name)


