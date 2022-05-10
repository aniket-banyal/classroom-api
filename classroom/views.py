from api.permissions import IsTeacherOrStudentReadOnly
from assignment.serializers import StudentSubmissionsSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classroom.permissions import (IsStudentInStudentSubmissions, IsTeacher,
                                   IsTeacherOrStudent)

from .models import Classroom
from .serializers import ClassroomSerializer, UserRoleSerializer


class ClassroomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classroom.objects.all()
    lookup_field = 'code'

    permission_classes = [IsAuthenticated, IsTeacherOrStudentReadOnly]
    serializer_class = ClassroomSerializer


class UserRole(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrStudent]

    def get(self, request, **kwargs):
        code = kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        user = request.user

        if classroom.is_user_a_teacher(user):
            role = 'teacher'
        elif classroom.is_user_a_student(user):
            role = 'student'

        serializer = UserRoleSerializer(data={'role': role})
        if serializer.is_valid():
            return Response(serializer.data)


class StudentSubmissions(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher, IsStudentInStudentSubmissions]
    serializer_class = StudentSubmissionsSerializer

    def get_queryset(self):
        code = self.kwargs['code']
        student_id = self.kwargs['student_id']
        classroom = get_object_or_404(Classroom, code=code)
        student = get_object_or_404(get_user_model(), id=student_id)

        return classroom.get_student_submissions(student)
