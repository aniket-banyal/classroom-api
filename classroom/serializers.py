from rest_framework import serializers
from user.serializers import UserSerializer

from .models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Classroom
        fields = ('teacher', 'name', 'subject', 'code')
