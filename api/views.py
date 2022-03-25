from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Announcement, Assignment, Classroom, Comment, Submission
from api.permissions import IsTeacherOrStudentReadOnly

from .serializers import (AnnouncementSerializer, AssignmentDetailSerializer,
                          AssignmentSerializer, ClassroomSerializer,
                          CommentSerializer, NewAnnouncementSerializer,
                          NewAssignmentSerializer, NewCommentSerializer,
                          NewSubmissionSerializer, StudentSubmissionSerializer,
                          StudentSubmissionsSerializer, SubmissionSerializer,
                          TeacherSubmissionSerializer, UserSerializer)


class ListCreateTeachingClassroom(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        return Classroom.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class ClassroomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classroom.objects.all()
    lookup_field = 'code'

    permission_classes = [IsAuthenticated, IsTeacherOrStudentReadOnly]
    serializer_class = ClassroomSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_class(request):
    code = request.data['code']
    classroom = get_object_or_404(Classroom, code=code)

    # check is user is already part of this classroom as a Teacher or Student
    user = request.user
    if user == classroom.teacher or classroom in user.enrolled_classrooms.all():
        return Response(status=status.HTTP_409_CONFLICT)

    classroom.students.add(user)
    serializer = ClassroomSerializer(classroom)

    return Response(serializer.data, status=status.HTTP_200_OK)


class ClassesEnrolled(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        return self.request.user.enrolled_classrooms.all()


class AllClasses(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        user = self.request.user
        classes_enrolled = user.enrolled_classrooms.all()
        classes_teaching = Classroom.objects.filter(teacher=user)
        return classes_enrolled.union(classes_teaching)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def announcements(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = AnnouncementSerializer(classroom.get_announcements(), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        request.data.update({"classroom": classroom.id})
        request.data.update({"author": user.id})

        serializer = NewAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(AnnouncementSerializer(serializer.instance).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def announcement_detail(request, code, id):
    classroom = get_object_or_404(Classroom, code=code)
    announcement = get_object_or_404(Announcement, id=id)
    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not (user == classroom.teacher or user == announcement.author):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = NewAnnouncementSerializer(announcement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AnnouncementSerializer(announcement).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def announcement_comments(request, code, id):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user
    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    announcement = get_object_or_404(Announcement, id=id)
    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CommentSerializer(announcement.get_comments(), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        request.data.update({"announcement": announcement.id})
        request.data.update({"author": user.id})

        serializer = NewCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(CommentSerializer(serializer.instance).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def announcement_comments_detail(request, code, announcement_id, comment_id):
    classroom = get_object_or_404(Classroom, code=code)
    comment = get_object_or_404(Comment, id=comment_id)
    announcement = get_object_or_404(Announcement, id=announcement_id)

    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if comment.announcement != announcement:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not (user == classroom.teacher or user == comment.author):
        return Response(status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def students(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(classroom.students.all(), many=True)
    return Response(serializer.data)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def students_detail(request, code, student_id):
    classroom = get_object_or_404(Classroom, code=code)
    student = get_object_or_404(get_user_model(), id=student_id)
    if student not in classroom.students.all():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'GET':
        if user != classroom.teacher:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(UserSerializer(student).data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if not(user == classroom.teacher or user == student):
            return Response(status=status.HTTP_403_FORBIDDEN)
        classroom.students.remove(student)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_role(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if user == classroom.teacher:
        return Response(data={'role': 'teacher'}, status=status.HTTP_200_OK)

    if classroom in user.enrolled_classrooms.all():
        return Response(data={'role': 'student'}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def assignments(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if request.method == 'GET':
        if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
            return Response(status=status.HTTP_403_FORBIDDEN)

        upcoming = request.query_params.get('upcoming')
        if upcoming:
            upcoming_assignment = classroom.get_upcoming_assignments()
            if upcoming_assignment is not None:
                serializer = AssignmentSerializer(upcoming_assignment)
                return Response(serializer.data)
            return Response({'data': None})

        serializer = AssignmentSerializer(classroom.assignment_set.all().order_by('-created_at'), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if user != classroom.teacher:
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
        if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = AssignmentDetailSerializer(assignment)
        return Response(serializer.data)

    elif request.method == 'PUT':
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
        if user != classroom.teacher:
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
        if user != classroom.teacher:
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = []
        for student in classroom.students.all():
            submission = get_user_submission(assignment, student)
            serializer = get_submission_data(assignment.due_date_time, student, submission)
            data.append(serializer.data)

        return Response(data)

    elif request.method == 'POST':
        if classroom not in user.enrolled_classrooms.all():
            return Response(status=status.HTTP_403_FORBIDDEN)

        request.data.update({"assignment": assignment.id})
        request.data.update({"student": user.id})

        serializer = NewSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_submission_data(due_date_time, student, submission):
    if submission is not None:
        return TeacherSubmissionSerializer({'student': student, 'submission': submission, 'status': submission.status})

    if due_date_time > datetime.now(timezone.utc):
        return TeacherSubmissionSerializer({'student': student, 'submission': submission, 'status': 'Assigned'})
    return TeacherSubmissionSerializer({'student': student, 'submission': submission, 'status': 'Missing'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_submission(request, code, assignment_id):
    classroom = get_object_or_404(Classroom, code=code)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'GET':
        if classroom not in user.enrolled_classrooms.all():
            return Response(status=status.HTTP_403_FORBIDDEN)

        submission = get_user_submission(assignment, user)
        if submission is None:
            if assignment.due_date_time > datetime.now(timezone.utc):
                return Response({'status': 'Assigned'})
            return Response({'status': 'Missing'})

        serializer = StudentSubmissionSerializer(submission)
        return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def submissions_detail(request, code, assignment_id, submission_id):
    classroom = get_object_or_404(Classroom, code=code)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'PATCH':
        if user != classroom.teacher:
            return Response(status=status.HTTP_403_FORBIDDEN)

        submission = get_object_or_404(Submission, id=submission_id)
        serializer = SubmissionSerializer(submission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_user_submission(assignment, user):
    all_submissions = assignment.submission_set.all()
    for submission in all_submissions:
        if submission.student == user:
            return submission
    return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_submissions(request, code, student_id):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user
    if user != classroom.teacher:
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        submissions = []
        student = get_object_or_404(get_user_model(), id=student_id)
        for assignment in classroom.assignment_set.all().order_by('-created_at'):
            submission = get_user_submission(assignment, student)
            serializer = get_student_submission_data(assignment, student, submission)
            submissions.append(serializer.data)

        return Response(submissions)


def get_student_submission_data(assignment, student, submission):
    if submission is not None:
        return StudentSubmissionsSerializer({'student': student, 'submission': submission, 'status': submission.status, 'assignment': assignment})

    if assignment.due_date_time > datetime.now(timezone.utc):
        return StudentSubmissionsSerializer({'student': student, 'submission': submission, 'status': 'Assigned', 'assignment': assignment})
    return StudentSubmissionsSerializer({'student': student, 'submission': submission, 'status': 'Missing', 'assignment': assignment})
