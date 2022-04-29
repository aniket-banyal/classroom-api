from datetime import datetime, timezone

from classroom.models import Classroom
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .helpers import get_submissions, get_user_submission
from .models import Assignment, Submission
from .serializers import (AssignmentDetailSerializer, AssignmentSerializer,
                          NewAssignmentSerializer, NewSubmissionSerializer,
                          StudentSubmissionSerializer, SubmissionSerializer)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def assignments(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if request.method == 'GET':
        if not classroom.is_user_part_of_classroom(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        upcoming = request.query_params.get('upcoming')
        if upcoming:
            upcoming_assignment = classroom.get_upcoming_assignments()
            if upcoming_assignment is not None:
                serializer = AssignmentSerializer(upcoming_assignment)
                return Response(serializer.data)
            return Response({'data': None})

        serializer = AssignmentSerializer(classroom.get_assignments(), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not classroom.is_user_a_teacher(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

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


@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def assignment_detail(request, code, assignment_id):
    classroom = get_object_or_404(Classroom, code=code)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'GET':
        if not classroom.is_user_part_of_classroom(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = AssignmentDetailSerializer(assignment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not classroom.is_user_a_teacher(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        request.data.update({"classroom": classroom.id})

        due_date_timestamp = int(request.data['due_date_time'])
        due_date_time = datetime.fromtimestamp(due_date_timestamp / 1000.0, timezone.utc)
        request.data.update({"due_date_time": due_date_time})

        serializer = NewAssignmentSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(AssignmentSerializer(assignment).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not classroom.is_user_a_teacher(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def submissions(request, code, assignment_id):
    classroom = get_object_or_404(Classroom, code=code)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'GET':
        if not classroom.is_user_a_teacher(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = get_submissions(classroom, assignment)
        return Response(data)

    elif request.method == 'POST':
        if not classroom.is_user_a_student(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def grade_submission(request, code, assignment_id, submission_id):
    classroom = get_object_or_404(Classroom, code=code)
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = get_object_or_404(Submission, id=submission_id)

    if assignment.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'PATCH':
        if not classroom.is_user_a_teacher(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            data = {'points': request.data['points']}
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = SubmissionSerializer(submission, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_submission(request, code, assignment_id):
    classroom = get_object_or_404(Classroom, code=code)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'GET':
        if not classroom.is_user_a_student(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        submission = get_user_submission(assignment, user)
        if submission is None:
            if assignment.due_date_time > datetime.now(timezone.utc):
                return Response({'status': 'Assigned'})
            return Response({'status': 'Missing'})

        serializer = StudentSubmissionSerializer(submission)
        return Response(serializer.data)
