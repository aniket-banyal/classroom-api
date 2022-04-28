from django.urls import path

from . import views

urlpatterns = [
    path('details', views.user_details, name='user_details'),
]
