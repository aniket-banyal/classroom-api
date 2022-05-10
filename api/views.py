from assignment.serializers import AssignmentWithClassroomSerializer
from classroom.models import Classroom
from classroom.serializers import ClassroomSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import ToReviewSerializer


class ListCreateTeachingClassroom(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        return Classroom.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


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


class AllAssignmentsToDo(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentWithClassroomSerializer

    def get_queryset(self):
        user = self.request.user
        all_assignments = []
        for classroom in user.enrolled_classrooms.all():
            all_assignments.extend(classroom.get_assignments_todo(user))

        all_assignments.sort(key=lambda assignement: assignement.due_date_time)
        return all_assignments


class AllToReview(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ToReviewSerializer

    def get_queryset(self):
        user = self.request.user
        data = []
        for classroom in user.teaching_classrooms.all():
            assignments = classroom.get_assignments()
            for assignment in assignments:
                num_turned_in = len(assignment.get_submissions_to_review())
                num_graded = len(assignment.get_submissions_graded())
                total_submissions = len(assignment.get_submissions())
                if num_graded < total_submissions:
                    data.append({'assignment': assignment, 'turned_in': num_turned_in, 'graded': num_graded})

        return data
