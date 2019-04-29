from django.contrib import admin
from .models import *
from django.db import models
from django.template.defaulttags import register


admin.site.register(Course)
admin.site.register(Task)
admin.site.register(Test)
admin.site.register(Comment)
admin.site.register(Language)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
