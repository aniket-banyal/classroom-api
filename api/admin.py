from django.contrib import admin

from api.models import Assignment, Classroom, Submission

admin.site.register(Classroom)
admin.site.register(Assignment)
admin.site.register(Submission)
