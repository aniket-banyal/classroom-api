from django.contrib.auth import get_user_model
from django.db import models


class Classroom(models.Model):
    teacher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    subject = models.CharField(max_length=50)

    def __str__(self):
        return f'Name: {self.name}-Subject: {self.subject}'
