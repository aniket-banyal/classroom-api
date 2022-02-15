from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Classroom


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')


class ClassroomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    students = UserSerializer(read_only=True, many=True, allow_empty=True)

    class Meta:
        model = Classroom
        fields = ('teacher', 'name', 'subject', 'code', 'students')
