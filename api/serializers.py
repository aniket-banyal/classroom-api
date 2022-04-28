from assignment.models import Assignment
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Classroom


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


class AssignmentWithClassroomSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer()

    class Meta:
        model = Assignment
        fields = ('id', 'title', 'created_at', 'edited_at', 'due_date_time', 'points', 'classroom')


class ToReviewSerializer(serializers.Serializer):
    assignment = AssignmentWithClassroomSerializer()
    turned_in = serializers.IntegerField(min_value=0)
    graded = serializers.IntegerField(min_value=0)
