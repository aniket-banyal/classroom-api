from django.urls import include, path

from . import views

urlpatterns = [
    path('user_details', views.user_details, name='user_details'),
    path('classes/<str:code>/user_role', views.user_role, name='user_role'),

    path('classes', views.AllClasses.as_view(), name='classes'),
    path('classes_enrolled', views.ClassesEnrolled.as_view(), name='classes_enrolled'),
    path('classes_teaching', views.ListCreateTeachingClassroom.as_view(), name='classes_teaching'),
    path('classes/<str:code>', views.ClassroomDetail.as_view(), name='classes_detail'),

    path('classes/<str:code>/announcements/', include('announcement.urls')),

    path('classes/<str:code>/assignments/', include('assignment.urls')),

    path('all_assignments_to_do', views.all_assignments_to_do, name='all_assignments_to_do'),
    path('all_to_review', views.all_to_review, name='all_to_review'),


    path('classes/<str:code>/student_submissions/<int:student_id>', views.get_student_submissions, name='student_submissions'),


    path('classes/<str:code>/students', views.students, name='students'),
    path('classes/<str:code>/students/<int:student_id>', views.students_detail, name='students_detail'),
]
