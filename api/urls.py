from django.urls import path

from . import views

urlpatterns = [
    path('classes_enrolled', views.classes_enrolled, name='classes_enrolled'),
    path('classes_teaching', views.ListCreateClassroom.as_view(), name='classes_teaching'),
    path('join_class', views.join_class, name='join_class'),
]
