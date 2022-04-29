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

    def get_assignments(self):
        return self.assignment_set.all().order_by('-created_at')

    def get_all_students(self):
        return self.students.all()

    def is_user_a_teacher(self, user):
        return user == self.teacher

    def is_user_a_student(self, user):
        return user in self.students.all()

    def is_user_part_of_classroom(self, user):
        return self.is_user_a_student(user) or self.is_user_a_teacher(user)

    def __str__(self):
        return f'Name: {self.name}-Subject: {self.subject}'
