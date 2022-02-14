from rest_framework import serializers

from api.models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)

    class Meta:
        model = Classroom
        fields = ('teacher', 'name', 'subject', 'code')
