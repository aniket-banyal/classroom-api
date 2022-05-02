from django.urls import path

from . import views

urlpatterns = [
    path('', views.Assignments.as_view(), name='assignments'),
    path('<int:assignment_id>', views.AssignmentDetail.as_view(), name='assignment_detail'),

    path('<int:assignment_id>/submissions', views.Submissions.as_view(), name='submissions'),
    path('<int:assignment_id>/submissions/<int:submission_id>', views.GradeSubmission.as_view(), name='grade_submission'),
    path('<int:assignment_id>/student_submission', views.student_submission, name='student_submission'),

]
