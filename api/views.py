from datetime import datetime, timezone

from assignment.helpers import get_user_submission
from assignment.serializers import AssignmentWithClassroomSerializer
from classroom.models import Classroom
from classroom.serializers import ClassroomSerializer
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ToReviewSerializer


class ListCreateTeachingClassroom(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        return Classroom.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


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
