from rest_framework import serializers
from user.serializers import UserSerializer

from .models import Announcement, Comment


class AnnouncementSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = ('id', 'text', 'author', 'created_at', 'edited_at')


class NewAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('text', 'classroom', 'author')

        read_only_fields = ['classroom', 'author']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'created_at')


class NewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('announcement', 'text', 'author')
