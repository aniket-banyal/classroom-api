from django.urls import path

from . import views

urlpatterns = [
    path('', views.Announcements.as_view(), name='announcements'),
    path('<int:announcement_id>', views.AnnouncementDetail.as_view(), name='announcement_detail'),

    path('<int:announcement_id>/comments', views.AnnouncementComments.as_view(), name='announcement_comments'),
    path('<int:announcement_id>/comments/<int:comment_id>', views.announcement_comments_detail, name='announcement_comments_detail'),
]
