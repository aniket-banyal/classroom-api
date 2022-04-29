from assignment.serializers import AssignmentWithClassroomSerializer
from rest_framework import serializers


class ToReviewSerializer(serializers.Serializer):
    assignment = AssignmentWithClassroomSerializer()
    turned_in = serializers.IntegerField(min_value=0)
    graded = serializers.IntegerField(min_value=0)
