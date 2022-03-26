from rest_framework.permissions import BasePermission


class IsTeacherOrStudent(BasePermission):
    def has_object_permission(self, request, view, classroom):
        user = request.user
        return classroom.is_user_part_of_classroom(user)


class IsTeacherOrStudentReadOnly(BasePermission):
    def has_object_permission(self, request, view, classroom):
        user = request.user
        if request.method == 'GET':
            return classroom.is_user_part_of_classroom(user)

        if request.method == 'DELETE' or request.method == 'PUT':
            return classroom.is_user_a_teacher(user)
