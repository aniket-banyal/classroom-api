from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Announcement, Assignment, Classroom, Comment, Submission


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('name', 'email')

    def get_name(self, user):
        return user.first_name + ' ' + user.last_name


class AnnouncementSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = ('id', 'text', 'author', 'created_at', 'edited_at')


class NewAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('text', 'classroom', 'author')


class ClassroomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Classroom
        fields = ('teacher', 'name', 'subject', 'code')


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
        fields = ('id', 'title', 'created_at', 'due_date_time')


class AssignmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('title', 'text', 'created_at', 'due_date_time')


class NewAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('title', 'text', 'classroom', 'due_date_time')

    def validate_due_date_time(self, value):
        if value < datetime.now(timezone.utc):
            raise serializers.ValidationError('Due date must be greater than current time')
        return value


class SubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ('student', 'text', 'created_at')


class TeacherSubmissionSerializer(serializers.Serializer):
    student = UserSerializer()
    submission = SubmissionSerializer()
    status = serializers.CharField()


class StudentSubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ('student', 'text', 'created_at', 'status')


class NewSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('text', 'assignment', 'student')
