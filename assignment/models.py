from api.models import Classroom
from django.contrib.auth import get_user_model
from django.db import models


class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    due_date_time = models.DateTimeField()
    points = models.PositiveSmallIntegerField()

    def get_submissions(self):
        return [submission for submission in self.submission_set.all()]

    def get_submissions_to_review(self):
        return [submission for submission in self.submission_set.all()
                if submission.status == 'Done' or submission.status == 'Submitted Late']

    def get_submissions_graded(self):
        return [submission for submission in self.submission_set.all()
                if submission.status == 'Graded']

    def get_student_submission(self, user):
        for submission in self.submission_set.all():
            if submission.student == user:
                return submission
        return None

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
