from django.contrib import admin

from api.models import Announcement, Assignment, Classroom, Comment

admin.site.register(Announcement)
admin.site.register(Classroom)
admin.site.register(Comment)
admin.site.register(Assignment)
