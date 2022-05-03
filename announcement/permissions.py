from classroom.models import Classroom
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import Announcement, Comment


class IsAnnouncementPartOfClassroom(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        announcement_id = view.kwargs['announcement_id']
        classroom = get_object_or_404(Classroom, code=code)
        announcement = get_object_or_404(Announcement, id=announcement_id)

        return announcement.classroom == classroom


class IsCommentPartOfAnnouncement(BasePermission):
    def has_permission(self, request, view):
        announcement_id = view.kwargs['announcement_id']
        comment_id = view.kwargs['comment_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)
        comment = get_object_or_404(Comment, id=comment_id)

        return comment.announcement == announcement


class IsTeacherOrAnnouncementAuthor(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        announcement_id = view.kwargs['announcement_id']
        classroom = get_object_or_404(Classroom, code=code)
        announcement = get_object_or_404(Announcement, id=announcement_id)

        user = request.user
        if request.method == 'DELETE' or request.method == 'PUT':
            return classroom.is_user_a_teacher(user) or announcement.author == user


class IsTeacherOrCommentAuthor(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        comment_id = view.kwargs['comment_id']
        classroom = get_object_or_404(Classroom, code=code)
        comment = get_object_or_404(Comment, id=comment_id)

        user = request.user
        if request.method == 'DELETE' or request.method == 'PUT':
            return classroom.is_user_a_teacher(user) or comment.author == user
