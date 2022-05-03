from classroom.models import Classroom
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from announcement.models import Announcement


class IsTeacherOrAnnouncementAuthor(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        announcement_id = view.kwargs['announcement_id']
        classroom = get_object_or_404(Classroom, code=code)
        announcement = get_object_or_404(Announcement, id=announcement_id)

        if announcement.classroom != classroom:
            return False

        user = request.user
        if request.method == 'DELETE' or request.method == 'PUT':
            return classroom.is_user_a_teacher(user) or announcement.author == user
