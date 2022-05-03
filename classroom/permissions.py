from rest_framework.permissions import BasePermission


class IsTeacherOrStudent(BasePermission):
    def has_object_permission(self, request, view, classroom):
        user = request.user
        return classroom.is_user_part_of_classroom(user)
