from django.urls import path

from . import views

urlpatterns = [
    path('user_details', views.user_details, name='user_details'),
    path('classes/<str:code>/user_role', views.user_role, name='user_role'),

    path('classes', views.AllClasses.as_view(), name='classes'),
    path('classes_enrolled', views.ClassesEnrolled.as_view(), name='classes_enrolled'),
    path('classes_teaching', views.ListCreateTeachingClassroom.as_view(), name='classes_teaching'),
    path('classes/<str:code>', views.ClassroomDetail.as_view(), name='classes_detail'),
    path('join_class', views.join_class, name='join_class'),

    path('classes/<str:code>/announcements', views.announcements, name='announcements'),
    path('classes/<str:code>/announcements/<int:id>', views.announcement_detail, name='announcement_detail'),

    path('classes/<str:code>/announcements/<int:id>/comments', views.announcement_comments, name='announcement_comments'),
    path('classes/<str:code>/announcements/<int:announcement_id>/comments/<int:comment_id>', views.announcement_comments_detail, name='announcement_comments_detail'),

    path('classes/<str:code>/assignments', views.assignments, name='assignments'),
    path('classes/<str:code>/assignments/<int:assignment_id>', views.assignment_detail, name='assignment_detail'),

    path('classes/<str:code>/assignments/<int:assignment_id>/submissions', views.submissions, name='submissions'),
    path('classes/<str:code>/assignments/<int:assignment_id>/submissions/<int:submission_id>', views.submissions_detail, name='submissions_detail'),

    path('classes/<str:code>/student_submissions/<int:student_id>', views.get_student_submissions, name='student_submissions'),
    path('classes/<str:code>/assignments/<int:assignment_id>/student_submission', views.student_submission, name='student_submission'),

    path('classes/<str:code>/students', views.students, name='students'),
    path('classes/<str:code>/students/<int:student_id>', views.students_detail, name='students_detail'),
]
