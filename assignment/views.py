from datetime import datetime, timezone

from classroom.models import Classroom
from classroom.permissions import IsTeacher
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from assignment.permissions import (IsAssignmentPartOfClassroom,
                                    IsStudentReadOnly,
                                    IsTeacherOrStudentPostOnlySubmissions,
                                    IsTeacherOrStudentReadOnly,
                                    IsTeacherOrStudentReadOnlyAssignmentDetail)

from .models import Assignment, Submission
from .serializers import (AssignmentDetailSerializer, AssignmentSerializer,
                          NewAssignmentSerializer, NewSubmissionSerializer,
                          StudentSubmissionSerializer, SubmissionSerializer,
                          TeacherSubmissionSerializer)


class Assignments(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacherOrStudentReadOnly]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        code = self.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)

        upcoming = self.request.query_params.get('upcoming')
        if upcoming:
            return classroom.get_upcoming_assignments()

        return classroom.get_assignments()

    def create(self, request, **kwargs):
        code = kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)

        request.data.update({"classroom": classroom.id})

        try:
            due_date_timestamp = int(request.data['due_date_time'])
        except (TypeError, ValueError):
            return Response({'due_date_time': ['Due date time is of invalid type']}, status=status.HTTP_400_BAD_REQUEST)

        due_date_time = datetime.fromtimestamp(due_date_timestamp / 1000.0, timezone.utc)
        request.data.update({"due_date_time": due_date_time})

        serializer = NewAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAssignmentPartOfClassroom, IsTeacherOrStudentReadOnlyAssignmentDetail]
    serializer_class = AssignmentDetailSerializer

    def get_object(self):
        assignment_id = self.kwargs['assignment_id']
        return get_object_or_404(Assignment, id=assignment_id)

    def update(self, request, **kwargs):
        code = kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        assignment = self.get_object()

        request.data.update({"classroom": classroom.id})

        try:
            due_date_timestamp = int(request.data['due_date_time'])
        except (TypeError, ValueError):
            return Response({'due_date_time': ['Due date time is of invalid type']}, status=status.HTTP_400_BAD_REQUEST)

        due_date_time = datetime.fromtimestamp(due_date_timestamp / 1000.0, timezone.utc)
        request.data.update({"due_date_time": due_date_time})

        serializer = NewAssignmentSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(AssignmentSerializer(assignment).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Submissions(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAssignmentPartOfClassroom, IsTeacherOrStudentPostOnlySubmissions]

    def get_serializer_class(self):
        request = self.request
        if request.method == 'GET':
            return TeacherSubmissionSerializer
        elif request.method == 'POST':
            return NewSubmissionSerializer

    def get_queryset(self):
        assignment_id = self.kwargs['assignment_id']
        assignment = get_object_or_404(Assignment, id=assignment_id)
        return assignment.get_all_submissions()

    def perform_create(self, serializer):
        assignment_id = self.kwargs['assignment_id']
        assignment = get_object_or_404(Assignment, id=assignment_id)

        request = self.request
        user = request.user
        # check if user has already submitted submission
        if assignment.get_student_submission(user) is not None:
            return Response(status=status.HTTP_409_CONFLICT)

        serializer.save(assignment=assignment, student=user)


class GradeSubmission(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAssignmentPartOfClassroom, IsTeacher]
    serializer_class = SubmissionSerializer

    def get_object(self):
        submission_id = self.kwargs['submission_id']
        return get_object_or_404(Submission, id=submission_id)

    def perform_update(self, serializer):
        try:
            points = self.request.data['points']
        except KeyError:
            raise ValidationError()
        serializer.save(points=points)


class StudentSubmission(APIView):
    permission_classes = [IsAuthenticated, IsAssignmentPartOfClassroom, IsStudentReadOnly]

    def get(self, request, **kwargs):
        assignment_id = kwargs['assignment_id']
        assignment = get_object_or_404(Assignment, id=assignment_id)
        user = request.user

        submission = assignment.get_student_submission(user)
        if submission is None:
            if assignment.due_date_time > datetime.now(timezone.utc):
                return Response({'status': 'Assigned'})
            return Response({'status': 'Missing'})

        serializer = StudentSubmissionSerializer(submission)
        return Response(serializer.data)
