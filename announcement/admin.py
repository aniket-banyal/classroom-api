from django.contrib import admin

from .models import Announcement, Comment

admin.site.register(Announcement)
admin.site.register(Comment)
