from datetime import datetime, timezone
from api.serializers import StudentSubmissionsSerializer, TeacherSubmissionSerializer


def get_submission_data(due_date_time, student, submission):
    if submission is not None:
        return TeacherSubmissionSerializer({'student': student, 'submission': submission, 'status': submission.status})

    if due_date_time > datetime.now(timezone.utc):
        return TeacherSubmissionSerializer({'student': student, 'submission': submission, 'status': 'Assigned'})
    return TeacherSubmissionSerializer({'student': student, 'submission': submission, 'status': 'Missing'})


def get_user_submission(assignment, user):
    all_submissions = assignment.submission_set.all()
    for submission in all_submissions:
        if submission.student == user:
            return submission
    return None


def get_student_submission_data(assignment, student, submission):
    if submission is not None:
        return StudentSubmissionsSerializer({'student': student, 'submission': submission, 'status': submission.status, 'assignment': assignment})

    if assignment.due_date_time > datetime.now(timezone.utc):
        return StudentSubmissionsSerializer({'student': student, 'submission': submission, 'status': 'Assigned', 'assignment': assignment})
    return StudentSubmissionsSerializer({'student': student, 'submission': submission, 'status': 'Missing', 'assignment': assignment})


def get_submissions(classroom, assignment):
    data = []
    for student in classroom.students.all():
        submission = get_user_submission(assignment, student)
        serializer = get_submission_data(assignment.due_date_time, student, submission)
        data.append(serializer.data)

    return data
