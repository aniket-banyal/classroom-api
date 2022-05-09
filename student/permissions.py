from classroom.models import Classroom
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission


class IsPartOfClassroomOrPostOnly(BasePermission):
    def has_permission(self, request, view):
        code = view.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)

        user = request.user
        if request.method == 'GET':
            return classroom.is_user_part_of_classroom(user)

        elif request.method == 'POST':
            return True
