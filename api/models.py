from datetime import datetime, timezone
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

    def get_upcoming_assignments(self):
        all_assignments = self.assignment_set.all().order_by('-due_date_time')
        upcoming_assignments = [assignment for assignment in all_assignments
                                if assignment.due_date_time > datetime.now(timezone.utc)]

        if len(upcoming_assignments) > 0:
            upcoming_assignments.sort(key=lambda assignment: assignment.due_date_time)
            return upcoming_assignments[0]

        return None

    def get_announcements(self):
        return self.announcement_set.all().order_by('-created_at')

    def __str__(self):
        return f'Name: {self.name}-Subject: {self.subject}'


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


class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    due_date_time = models.DateTimeField()
    points = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.title} -  {self.text}'


class Submission(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    points = models.FloatField(null=True, blank=True)

    @property
    def status(self):
        if self.points:
            return 'Graded'

        if self.created_at <= self.assignment.due_date_time:
            return 'Done'
        return 'Submitted Late'

    def __str__(self):
        return f'{self.url}'
