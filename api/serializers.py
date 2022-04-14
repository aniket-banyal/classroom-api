from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Announcement, Assignment, Classroom, Comment, Submission


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'name', 'email')

    def get_name(self, user):
        return user.first_name + ' ' + user.last_name


class ClassroomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Classroom
        fields = ('teacher', 'name', 'subject', 'code')


class AnnouncementSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = ('id', 'text', 'author', 'created_at', 'edited_at')


class NewAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('text', 'classroom', 'author')


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'created_at')


class NewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('announcement', 'text', 'author')


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('id', 'title', 'created_at', 'edited_at', 'due_date_time', 'points')


class AssignmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('title', 'text', 'created_at', 'edited_at', 'due_date_time', 'points')


class NewAssignmentSerializer(serializers.ModelSerializer):
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


class TeacherSubmissionSerializer(serializers.Serializer):
    student = UserSerializer()
    submission = SubmissionSerializer()
    status = serializers.CharField()


class StudentSubmissionsSerializer(serializers.Serializer):
    submission = SubmissionSerializer()
    status = serializers.CharField()
    assignment = AssignmentSerializer()


class StudentSubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ('student', 'url', 'created_at', 'status', 'points')


class NewSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('url', 'assignment', 'student')


class ToReviewSerializer(serializers.Serializer):
    assignment = AssignmentWithClassroomSerializer()
    turned_in = serializers.IntegerField(min_value=0)
    graded = serializers.IntegerField(min_value=0)
