from classroom.models import Classroom
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
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


@extend_schema(responses=UserSerializer)
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def students_detail(request, code, student_id):
    classroom = get_object_or_404(Classroom, code=code)
    student = get_object_or_404(get_user_model(), id=student_id)
    if student not in classroom.students.all():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'GET':
        if not classroom.is_user_a_teacher(user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(UserSerializer(student).data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if not(classroom.is_user_a_teacher(user) or user == student):
            return Response(status=status.HTTP_403_FORBIDDEN)
        classroom.students.remove(student)
        return Response(status=status.HTTP_204_NO_CONTENT)
