from classroom.models import Classroom
from classroom.permissions import IsTeacher
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from user.serializers import UserSerializer

from student.permissions import IsPartOfClassroomOrPostOnly


class Students(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsPartOfClassroomOrPostOnly]
    serializer_class = UserSerializer

    def get_queryset(self):
        code = self.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        return classroom.get_all_students()

    def post(self, request, **kwargs):
        code = kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        user = request.user

        # check if user is already part of this classroom
        if classroom.is_user_part_of_classroom(user):
            return Response(status=status.HTTP_409_CONFLICT)

        classroom.students.add(user)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentsDetail(generics.ListAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = UserSerializer

    def get_object(self):
        student_id = self.kwargs['student_id']
        return get_object_or_404(get_user_model(), id=student_id)

    def destroy(self, request, **kwargs):
        code = kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)

        student = self.get_object()
        classroom.students.remove(student)
        return Response(status=status.HTTP_204_NO_CONTENT)
