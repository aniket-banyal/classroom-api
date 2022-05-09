from classroom.models import Classroom
from classroom.permissions import IsTeacherOrStudent
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from announcement.permissions import (IsAnnouncementPartOfClassroom,
                                      IsCommentPartOfAnnouncement,
                                      IsTeacherOrAnnouncementAuthor,
                                      IsTeacherOrCommentAuthor)

from .models import Announcement, Comment
from .serializers import (AnnouncementSerializer, CommentSerializer,
                          NewAnnouncementSerializer, NewCommentSerializer)


class Announcements(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacherOrStudent]

    def get_serializer_class(self):
        method = self.request.method
        if method == 'GET':
            return AnnouncementSerializer
        elif method == 'POST':
            return NewAnnouncementSerializer

    def get_queryset(self):
        code = self.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        return classroom.get_announcements()

    def perform_create(self, serializer):
        code = self.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        serializer.save(classroom=classroom, author=self.request.user)


class AnnouncementDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAnnouncementPartOfClassroom, IsTeacherOrAnnouncementAuthor]
    serializer_class = NewAnnouncementSerializer

    def get_object(self):
        announcement_id = self.kwargs['announcement_id']
        return get_object_or_404(Announcement, id=announcement_id)

    def perform_update(self, serializer):
        code = self.kwargs['code']
        classroom = get_object_or_404(Classroom, code=code)
        serializer.save(classroom=classroom, author=self.request.user)


class AnnouncementComments(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAnnouncementPartOfClassroom, IsTeacherOrStudent]

    def get_serializer_class(self):
        method = self.request.method
        if method == 'GET':
            return CommentSerializer
        elif method == 'POST':
            return NewCommentSerializer

    def get_queryset(self):
        announcement_id = self.kwargs['announcement_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)
        return announcement.get_comments()

    def perform_create(self, serializer):
        announcement_id = self.kwargs['announcement_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)
        serializer.save(announcement=announcement, author=self.request.user)


class AnnouncementCommentDelete(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAnnouncementPartOfClassroom, IsCommentPartOfAnnouncement, IsTeacherOrCommentAuthor]

    def get_object(self):
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, id=comment_id)
