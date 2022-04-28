from datetime import datetime, timezone
from assignment.serializers import StudentSubmissionsSerializer, TeacherSubmissionSerializer


def get_user_submission(assignment, user):
    all_submissions = assignment.submission_set.all()
    for submission in all_submissions:
        if submission.student == user:
            return submission
    return None


def get_submission_data(due_date_time, student, submission):
    if submission is not None:
        status = submission.status

    elif due_date_time > datetime.now(timezone.utc):
        status = 'Assigned'
    else:
        status = 'Missing'

    return TeacherSubmissionSerializer({'student': student, 'submission': submission, 'status': status})


def get_submissions(classroom, assignment):
    data = []
    for student in classroom.students.all():
        submission = get_user_submission(assignment, student)
        serializer = get_submission_data(assignment.due_date_time, student, submission)
        data.append(serializer.data)

    return data


def get_student_submission_data(assignment, student, submission):
    if submission is not None:
        status = submission.status

    elif assignment.due_date_time > datetime.now(timezone.utc):
        status = 'Assigned'
    else:
        status = 'Missing'

    return StudentSubmissionsSerializer({'student': student, 'submission': submission, 'assignment': assignment, 'status': status})
