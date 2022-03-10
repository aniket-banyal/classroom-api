from rest_framework.permissions import BasePermission


class IsTeacherOrStudent(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user == obj.teacher or obj in user.enrolled_classrooms.all()
