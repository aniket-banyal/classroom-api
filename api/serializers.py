from rest_framework import serializers

from api.models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ('id', 'teacher', 'name', 'subject')
