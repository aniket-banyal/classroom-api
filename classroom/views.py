from api.permissions import IsTeacherOrStudentReadOnly
from assignment.helpers import get_student_submission_data, get_user_submission
from assignment.serializers import StudentSubmissionsSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classroom.permissions import IsTeacherOrStudent

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


@extend_schema(responses=StudentSubmissionsSerializer(many=True))
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_submissions(request, code, student_id):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user
    if not classroom.is_user_a_teacher(user):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        submissions = []
        student = get_object_or_404(get_user_model(), id=student_id)
        for assignment in classroom.assignment_set.all().order_by('-created_at'):
            submission = get_user_submission(assignment, student)
            serializer = get_student_submission_data(assignment, student, submission)
            submissions.append(serializer.data)

        return Response(submissions)
