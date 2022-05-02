from datetime import datetime, timezone

from classroom.models import Classroom
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from assignment.permissions import (IsAssignmentPartOfClassroom,
                                    IsStudentReadOnly,
                                    IsTeacherOrStudentPostOnlySubmissions,
                                    IsTeacherOrStudentReadOnly,
                                    IsTeacherOrStudentReadOnlyAssignmentDetail)

from .helpers import get_submissions, get_user_submission
from .models import Assignment, Submission
from .serializers import (AssignmentDetailSerializer, AssignmentSerializer,
                          NewAssignmentSerializer, NewSubmissionSerializer,
                          StudentSubmissionSerializer, SubmissionSerializer)


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
        except TypeError:
            return Response({'due_date_time': ['Due date time is of invalid type']}, status=status.HTTP_400_BAD_REQUEST)

        due_date_time = datetime.fromtimestamp(due_date_timestamp / 1000.0, timezone.utc)
        request.data.update({"due_date_time": due_date_time})

        serializer = NewAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentDetail(APIView):
    permission_classes = [IsAuthenticated, IsAssignmentPartOfClassroom, IsTeacherOrStudentReadOnlyAssignmentDetail]

    def get(self, request, code, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        serializer = AssignmentDetailSerializer(assignment)
        return Response(serializer.data)

    def put(self, request, code, assignment_id):
        classroom = get_object_or_404(Classroom, code=code)
        assignment = get_object_or_404(Assignment, id=assignment_id)

        request.data.update({"classroom": classroom.id})

        due_date_timestamp = int(request.data['due_date_time'])
        due_date_time = datetime.fromtimestamp(due_date_timestamp / 1000.0, timezone.utc)
        request.data.update({"due_date_time": due_date_time})

        serializer = NewAssignmentSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(AssignmentSerializer(assignment).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Submissions(APIView):
    permission_classes = [IsAuthenticated, IsAssignmentPartOfClassroom, IsTeacherOrStudentPostOnlySubmissions]

    def get(self, request, code, assignment_id):
        classroom = get_object_or_404(Classroom, code=code)
        assignment = get_object_or_404(Assignment, id=assignment_id)

        data = get_submissions(classroom, assignment)
        return Response(data)

    def post(self, request, code, assignment_id):
        user = request.user
        assignment = get_object_or_404(Assignment, id=assignment_id)

        # check if user has already submitted submission
        if assignment.get_student_submission(user) is not None:
            return Response(status=status.HTTP_409_CONFLICT)

        request.data.update({"assignment": assignment.id})
        request.data.update({"student": user.id})

        serializer = NewSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GradeSubmission(APIView):
    permission_classes = [IsAuthenticated, IsAssignmentPartOfClassroom, IsTeacherOrStudentPostOnlySubmissions]

    def patch(self, request, code, assignment_id, submission_id):
        submission = get_object_or_404(Submission, id=submission_id)

        try:
            data = {'points': request.data['points']}
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = SubmissionSerializer(submission, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentSubmission(APIView):
    permission_classes = [IsAuthenticated, IsAssignmentPartOfClassroom, IsStudentReadOnly]

    def get(self, request, code, assignment_id):
        user = request.user
        assignment = get_object_or_404(Assignment, id=assignment_id)

        submission = get_user_submission(assignment, user)
        if submission is None:
            if assignment.due_date_time > datetime.now(timezone.utc):
                return Response({'status': 'Assigned'})
            return Response({'status': 'Missing'})

        serializer = StudentSubmissionSerializer(submission)
        return Response(serializer.data)
