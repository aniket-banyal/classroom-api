from classroom.models import Classroom
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission


class IsTeacherOrStudentReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        classroom = get_object_or_404(Classroom, code=view.kwargs['code'])

        if request.method == 'GET':
            return classroom.is_user_part_of_classroom(user)

        if request.method == 'POST' or request.method == 'DELETE' or request.method == 'PUT':
            return classroom.is_user_a_teacher(user)
