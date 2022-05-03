from classroom.models import Classroom
from classroom.permissions import IsTeacherOrStudent
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from announcement.permissions import IsTeacherOrAnnouncementAuthor

from .models import Announcement, Comment
from .serializers import (AnnouncementSerializer, CommentSerializer,
                          NewAnnouncementSerializer, NewCommentSerializer)


class Announcements(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacherOrStudent]
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        code = self.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        return classroom.get_announcements()

    def create(self, request, **kwargs):
        code = self.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        request.data.update({"classroom": classroom.id})
        request.data.update({"author": request.user.id})

        serializer = NewAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(AnnouncementSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnnouncementDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAnnouncementAuthor]
    serializer_class = NewAnnouncementSerializer

    def get_object(self):
        announcement_id = self.kwargs['announcement_id']
        return get_object_or_404(Announcement, id=announcement_id)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)

    def destroy(self, request, **kwargs):
        announcement = self.get_object()
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def announcement_comments(request, code, id):
    classroom = get_object_or_404(Classroom, code=code)
    user = request.user
    if not classroom.is_user_part_of_classroom(user):
        return Response(status=status.HTTP_403_FORBIDDEN)

    announcement = get_object_or_404(Announcement, id=id)
    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CommentSerializer(announcement.get_comments(), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        request.data.update({"announcement": announcement.id})
        request.data.update({"author": user.id})

        serializer = NewCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(CommentSerializer(serializer.instance).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def announcement_comments_detail(request, code, announcement_id, comment_id):
    classroom = get_object_or_404(Classroom, code=code)
    comment = get_object_or_404(Comment, id=comment_id)
    announcement = get_object_or_404(Announcement, id=announcement_id)

    if announcement.classroom != classroom:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if comment.announcement != announcement:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not (classroom.is_user_a_teacher(user) or user == comment.author):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
