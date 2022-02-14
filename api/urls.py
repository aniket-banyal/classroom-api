from django.urls import path

from . import views

urlpatterns = [
    path('', views.ListCreateClassroom.as_view(), name='index'),
]
