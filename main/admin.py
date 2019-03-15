from django.contrib import admin
from .models import Course, Task, Test, Comment
from tinymce.widgets import TinyMCE
from django.db import models


admin.site.register(Course)
admin.site.register(Task)
admin.site.register(Test)
admin.site.register(Comment)