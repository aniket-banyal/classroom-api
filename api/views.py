from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Announcement, Classroom

from .serializers import (AnnouncementSerializer, ClassroomSerializer,
                          CommentSerializer, NewAnnouncementSerializer,
                          NewCommentSerializer, UserSerializer)


class ListCreateClassroom(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classrooms = Classroom.objects.filter(teacher=request.user)
        serializer = ClassroomSerializer(classrooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        request.data.update({"teacher": request.user.id})

        serializer = ClassroomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_class(request):
    code = request.data['code']
    classroom = Classroom.objects.get(code=code)
    classroom.students.add(request.user)
    serializer = ClassroomSerializer(classroom)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def classes_enrolled(request):
    student = request.user

    # using related_name 'enrolled_classrooms' specified in Classroom model
    classes_enrolled = student.enrolled_classrooms.all()
    serializer = ClassroomSerializer(classes_enrolled, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def classes(request, code):
    classroom = Classroom.objects.get(code=code)
    user = request.user

    if user == classroom.teacher or classroom in user.enrolled_classrooms.all():
        serializer = ClassroomSerializer(classroom)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def announcements(request, code):
    classroom = Classroom.objects.get(code=code)
    user = request.user
    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = AnnouncementSerializer(classroom.announcement_set.all(), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        request.data.update({"classroom": classroom.id})
        request.data.update({"author": user.id})

        serializer = NewAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def students(request, code):
    classroom = Classroom.objects.get(code=code)
    user = request.user
    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(classroom.students.all(), many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def announcement_comments(request, code, id):
    classroom = Classroom.objects.get(code=code)
    user = request.user
    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    announcement = Announcement.objects.get(id=id)
    # announcement should be part of this classroom
    if announcement not in classroom.announcement_set.all():
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        comments = announcement.comment_set.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        request.data.update({"announcement": announcement.id})
        request.data.update({"author": user.id})

        serializer = NewCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
