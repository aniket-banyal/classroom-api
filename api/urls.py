from django.urls import path

from . import views

urlpatterns = [
    path('', views.ListCreateClassroom.as_view(), name='index'),
    path('join_class', views.join_class, name='join_class'),
]
