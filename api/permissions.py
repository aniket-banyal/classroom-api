from rest_framework.permissions import BasePermission


class IsTeacherOrStudent(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user == obj.teacher or obj in user.enrolled_classrooms.all()


class IsTeacherOrStudentReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method == 'GET':
            return user == obj.teacher or obj in user.enrolled_classrooms.all()

        if request.method == 'DELETE':
            return user == obj.teacher
