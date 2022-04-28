from django.urls import path

from . import views

urlpatterns = [
    path('', views.students, name='students'),
    path('<int:student_id>', views.students_detail, name='students_detail'),
]
