from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string


class Classroom(models.Model):
    CODE_LEN = 16
    teacher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    subject = models.CharField(max_length=50)
    code = models.CharField(max_length=CODE_LEN, unique=True)

    def save(self, *args, **kwargs):
        while True:
            self.code = get_random_string(length=self.CODE_LEN)
            if not Classroom.objects.filter(code=self.code).exists():
                break

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Name: {self.name}-Subject: {self.subject}'
