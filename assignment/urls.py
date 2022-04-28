from django.urls import path

from . import views

urlpatterns = [
    path('', views.assignments, name='assignments'),
    path('<int:assignment_id>', views.assignment_detail, name='assignment_detail'),

    path('<int:assignment_id>/submissions', views.submissions, name='submissions'),
    path('<int:assignment_id>/submissions/<int:submission_id>', views.grade_submission, name='grade_submission'),

]