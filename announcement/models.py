from api.models import Classroom
from django.contrib.auth import get_user_model
from django.db import models


class Announcement(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def get_comments(self):
        return self.comment_set.all().order_by('created_at')

    def __str__(self):
        return self.text


class Comment(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
