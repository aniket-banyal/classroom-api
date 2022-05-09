from django.urls import path

from . import views

urlpatterns = [
    path('details', views.UserDetails.as_view(), name='user_details'),
]
