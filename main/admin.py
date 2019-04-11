from django.contrib import admin
from .models import Course, Task, Test, Comment
from tinymce.widgets import TinyMCE
from django.db import models
from django.template.defaulttags import register


admin.site.register(Course)
admin.site.register(Task)
admin.site.register(Test)
admin.site.register(Comment)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)