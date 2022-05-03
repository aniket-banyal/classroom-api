from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import Classroom


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)

        user = request.user
        return classroom.is_user_a_teacher(user)


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)

        user = request.user
        return classroom.is_user_a_student(user)


class IsStudentInStudentSubmissions(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        student_id = view.kwargs['student_id']

        classroom = get_object_or_404(Classroom, code=code)
        student = get_object_or_404(get_user_model(), id=student_id)

        return classroom.is_user_a_student(student)


class IsTeacherOrStudent(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)

        user = request.user
        return classroom.is_user_part_of_classroom(user)
