from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.helpers import (get_student_submission_data, get_submissions,
                         get_user_submission)
from api.models import Announcement, Assignment, Classroom, Comment, Submission
from api.permissions import IsTeacherOrStudentReadOnly

from .serializers import (AnnouncementSerializer, AssignmentDetailSerializer,
                          AssignmentSerializer,
                          AssignmentWithClassroomSerializer,
                          ClassroomSerializer, CommentSerializer,
                          NewAnnouncementSerializer, NewAssignmentSerializer,
                          NewCommentSerializer, NewSubmissionSerializer,
                          StudentSubmissionSerializer, StudentSubmissionsSerializer, SubmissionSerializer,
                          ToReviewSerializer, UserSerializer)


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


@extend_schema(
    request=inline_serializer(
        name='JoinClassroomSerializer',
        fields={'code': serializers.CharField()}
    ),
    responses=ClassroomSerializer
)
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


@extend_schema(responses=UserSerializer)
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

    if not classroom.is_user_part_of_classroom(user):
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
            return Response(AnnouncementSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def announcement_detail(request, code, id):
    classroom = get_object_or_404(Classroom, code=code)
    announcement = get_object_or_404(Announcement, id=id)
    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not (classroom.is_user_a_teacher(user) or user == announcement.author):
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
    if not classroom.is_user_part_of_classroom(user):
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
    if not (classroom.is_user_a_teacher(user) or user == comment.author):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses=UserSerializer(many=True))
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def students(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if request.method == 'GET':

        if not classroom.is_user_part_of_classroom(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(classroom.get_all_students(), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # check is user is already part of this classroom as a Teacher or Student
        if classroom.is_user_part_of_classroom(user):
            return Response(status=status.HTTP_409_CONFLICT)

        classroom.students.add(user)
        serializer = ClassroomSerializer(classroom)

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


@extend_schema(
    responses=inline_serializer(
        name='UserRoleSerializer',
        fields={'role': serializers.CharField()}
    )
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_role(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if classroom.is_user_a_teacher(user):
        return Response(data={'role': 'teacher'}, status=status.HTTP_200_OK)

    if classroom.is_user_a_student(user):
        return Response(data={'role': 'student'}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_403_FORBIDDEN)


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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def grade_submission(request, code, assignment_id, submission_id):
    classroom = get_object_or_404(Classroom, code=code)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if request.method == 'PATCH':
        if not classroom.is_user_a_teacher(user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        submission = get_object_or_404(Submission, id=submission_id)
        serializer = SubmissionSerializer(submission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@extend_schema(responses=AssignmentWithClassroomSerializer(many=True))
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_assignments_to_do(request):
    user = request.user

    if request.method == 'GET':
        all_assignments = []
        for classroom in user.enrolled_classrooms.all():
            assignments = classroom.get_assignments()

            for assignment in assignments:
                submission = get_user_submission(assignment, user)
                if submission is None:
                    if assignment.due_date_time > datetime.now(timezone.utc):
                        all_assignments.append(assignment)

        serializer = AssignmentWithClassroomSerializer(all_assignments, many=True)
        return Response(serializer.data)


@extend_schema(responses=ToReviewSerializer(many=True))
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_to_review(request):
    user = request.user

    if request.method == 'GET':
        data = []
        for classroom in user.classroom_set.all():
            assignments = classroom.get_assignments()
            for assignment in assignments:
                num_turned_in = len(assignment.get_submissions_to_review())
                num_graded = len(assignment.get_submissions_graded())
                total_submissions = len(assignment.get_submissions())
                if num_graded < total_submissions:
                    data.append({'assignment': assignment, 'turned_in': num_turned_in, 'graded': num_graded})

        serializer = ToReviewSerializer(data, many=True)
        return Response(serializer.data)
