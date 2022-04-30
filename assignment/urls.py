from django.urls import path

from . import views

urlpatterns = [
    path('', views.Assignments.as_view(), name='assignments'),
    path('<int:assignment_id>', views.assignment_detail, name='assignment_detail'),

    path('<int:assignment_id>/submissions', views.submissions, name='submissions'),
    path('<int:assignment_id>/submissions/<int:submission_id>', views.grade_submission, name='grade_submission'),
    path('<int:assignment_id>/student_submission', views.student_submission, name='student_submission'),

]
