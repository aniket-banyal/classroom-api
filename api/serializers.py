from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Announcement, Classroom


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('id', 'text')


class ClassroomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)

    class Meta:
        model = Classroom
        fields = ('teacher', 'name', 'subject', 'code')

class ClassroomDetailsSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    students = UserSerializer(read_only=True, many=True, allow_empty=True)
    announcements = AnnouncementSerializer(source='announcement_set', many=True, allow_empty=True)

    class Meta:
        model = Classroom
        fields = ('teacher', 'name', 'subject', 'code', 'students', 'announcements')
