from datetime import datetime, timezone

from classroom.serializers import ClassroomSerializer
from rest_framework import serializers
from user.serializers import UserSerializer

from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('id', 'title', 'created_at', 'edited_at', 'due_date_time', 'points')


class AssignmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('title', 'text', 'created_at', 'edited_at', 'due_date_time', 'points')


class NewAssignmentSerializer(serializers.ModelSerializer):
    due_date_time = serializers.DateTimeField(read_only=True)
    classroom = ClassroomSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ('title', 'text', 'classroom', 'due_date_time', 'points')

    def validate_due_date_time(self, value):
        if value < datetime.now(timezone.utc):
            raise serializers.ValidationError('Due date must be greater than current time')
        return value

    def validate_points(self, value):
        if value < 0:
            raise serializers.ValidationError('Points must be greater than or equal to Zero')
        return value


class AssignmentWithClassroomSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer()

    class Meta:
        model = Assignment
        fields = ('id', 'title', 'created_at', 'edited_at', 'due_date_time', 'points', 'classroom')


class SubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ('id', 'student', 'url', 'created_at', 'points')

    def validate_points(self, value):
        if value > self.instance.assignment.points:
            raise serializers.ValidationError("Submission's points must be less than or equal to assignment's points")
        return value


class NewSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('url', 'assignment', 'student')


class TeacherSubmissionSerializer(serializers.Serializer):
    student = UserSerializer()
    submission = SubmissionSerializer()
    status = serializers.CharField()


class StudentSubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ('student', 'url', 'created_at', 'status', 'points')


class StudentSubmissionsSerializer(serializers.Serializer):
    submission = SubmissionSerializer()
    status = serializers.CharField()
    assignment = AssignmentSerializer()
