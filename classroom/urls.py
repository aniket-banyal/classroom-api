from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.ClassroomDetail.as_view(), name='classes_detail'),

    path('user_role', views.UserRole.as_view(), name='user_role'),

    path('announcements/', include('announcement.urls')),

    path('assignments/', include('assignment.urls')),

    path('students/', include('student.urls')),

    path('student_submissions/<int:student_id>', views.StudentSubmissions.as_view(), name='student_submissions'),
]
