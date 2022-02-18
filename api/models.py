from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string


class Classroom(models.Model):
    CODE_LEN = 16
    teacher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    subject = models.CharField(max_length=50)
    code = models.CharField(max_length=CODE_LEN, unique=True)
    students = models.ManyToManyField(get_user_model(), related_name='enrolled_classrooms')

    def save(self, *args, **kwargs):
        # save is also called when a classroom is updated, so this check prevents updation of code
        if self.code == '':
            while True:
                self.code = get_random_string(length=self.CODE_LEN)
                if not Classroom.objects.filter(code=self.code).exists():
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Name: {self.name}-Subject: {self.subject}'


class Announcement(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    @property
    def author_name(self):
        return self.author.first_name + ' ' + self.author.last_name

    def __str__(self):
        return self.text
