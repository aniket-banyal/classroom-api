from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Announcement, Classroom, Comment


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('name', 'email')

    def get_name(self, user):
        return user.first_name + ' ' + user.last_name


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField()

    class Meta:
        model = Announcement
        fields = ('id', 'text', 'author_name', 'created_at')


class NewAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('text', 'classroom', 'author')


class ClassroomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)

    class Meta:
        model = Classroom
        fields = ('teacher', 'name', 'subject', 'code')


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author_name')


class NewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('announcement', 'text', 'author')
