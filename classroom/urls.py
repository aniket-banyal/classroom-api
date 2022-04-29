from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.ClassroomDetail.as_view(), name='classes_detail'),

    path('user_role', views.user_role, name='user_role'),

    path('announcements/', include('announcement.urls')),

    path('assignments/', include('assignment.urls')),

    path('students/', include('student.urls')),

    path('student_submissions/<int:student_id>', views.get_student_submissions, name='student_submissions'),
]
