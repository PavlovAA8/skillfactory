from django.contrib import admin
from .models import Category, Announcement, Comment, ScheduledMessage, AnnouncementImage

admin.site.register(Category)
admin.site.register(Announcement)
admin.site.register(Comment)
admin.site.register(ScheduledMessage)
admin.site.register(AnnouncementImage)

