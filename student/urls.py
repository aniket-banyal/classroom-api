from django.urls import path

from . import views

urlpatterns = [
    path('', views.Students.as_view(), name='students'),
    path('<int:student_id>', views.StudentsDetail.as_view(), name='students_detail'),
]
