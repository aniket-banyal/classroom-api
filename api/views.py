from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Announcement, Classroom, Comment

from .serializers import (AnnouncementSerializer, AssignmentSerializer,
                          ClassroomSerializer, CommentSerializer,
                          NewAnnouncementSerializer, NewAssignmentSerializer,
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
    classroom = get_object_or_404(Classroom, code=code)

    # check is user is already part of this classroom as a Teacher or Student
    user = request.user
    if user == classroom.teacher or classroom in user.enrolled_classrooms.all():
        return Response(status=status.HTTP_409_CONFLICT)

    classroom.students.add(user)
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
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if user == classroom.teacher or classroom in user.enrolled_classrooms.all():
        serializer = ClassroomSerializer(classroom)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def announcements(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = AnnouncementSerializer(classroom.announcement_set.all().order_by('-created_at'), many=True)
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
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(classroom.students.all(), many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def announcement_comments(request, code, id):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
        return Response(status=status.HTTP_403_FORBIDDEN)

    announcement = get_object_or_404(Announcement, id=id)
    # announcement should be part of this classroom
    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        comments = announcement.comment_set.all().order_by('created_at')
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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def announcement_comments_detail(request, code, announcement_id, comment_id):
    classroom = get_object_or_404(Classroom, code=code)
    announcement = get_object_or_404(Announcement, id=announcement_id)

    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    comment = get_object_or_404(Comment, id=comment_id)
    if comment.announcement != announcement:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not (user == classroom.teacher or user == comment.author):
        return Response(status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def announcement_detail(request, code, id):
    classroom = get_object_or_404(Classroom, code=code)
    announcement = get_object_or_404(Announcement, id=id)

    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not (user == classroom.teacher or user == announcement.author):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = NewAnnouncementSerializer(announcement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AnnouncementSerializer(announcement).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_role(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if user == classroom.teacher:
        return Response(data={'role': 'teacher'}, status=status.HTTP_200_OK)

    if classroom in user.enrolled_classrooms.all():
        return Response(data={'role': 'student'}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def assignments(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user

    if request.method == 'GET':
        if not (user == classroom.teacher or classroom in user.enrolled_classrooms.all()):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = AssignmentSerializer(classroom.assignment_set.all().order_by('-created_at'), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if user != classroom.teacher:
            return Response(status=status.HTTP_403_FORBIDDEN)

        request.data.update({"classroom": classroom.id})

        serializer = NewAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
