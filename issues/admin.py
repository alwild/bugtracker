from bugtracker.issues.models import *
from django.contrib import admin

admin.site.register(Status)
admin.site.register(Severity)
admin.site.register(Category)
admin.site.register(Issue)
admin.site.register(Project)