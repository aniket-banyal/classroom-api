from classroom.models import Classroom
from classroom.permissions import IsTeacherOrStudent
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from announcement.permissions import (IsAnnouncementPartOfClassroom,
                                      IsCommentPartOfAnnouncement,
                                      IsTeacherOrAnnouncementAuthor,
                                      IsTeacherOrCommentAuthor)

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
    permission_classes = [IsAuthenticated, IsAnnouncementPartOfClassroom, IsTeacherOrAnnouncementAuthor]
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


class AnnouncementComments(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAnnouncementPartOfClassroom, IsTeacherOrStudent]
    serializer_class = CommentSerializer

    def get_queryset(self):
        announcement_id = self.kwargs['announcement_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)
        return announcement.get_comments()

    def create(self, request, **kwargs):
        announcement_id = kwargs['announcement_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)

        request.data.update({"announcement": announcement.id})
        request.data.update({"author": request.user.id})

        serializer = NewCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(CommentSerializer(serializer.instance).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnnouncementCommentDelete(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAnnouncementPartOfClassroom, IsCommentPartOfAnnouncement, IsTeacherOrCommentAuthor]

    def get_object(self):
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, id=comment_id)

    def destroy(self, request, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
