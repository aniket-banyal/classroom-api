from django.urls import path

from . import views

urlpatterns = [
    path('', views.announcements, name='announcements'),
    path('<int:id>', views.announcement_detail, name='announcement_detail'),

    path('<int:id>/comments', views.announcement_comments, name='announcement_comments'),
    path('<int:announcement_id>/comments/<int:comment_id>', views.announcement_comments_detail, name='announcement_comments_detail'),
]
