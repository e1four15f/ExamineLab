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


@register.filter
def check_all(dictionary, key=''):
    if dictionary:
        if all(dictionary.values()):
            return True
        else:
            return {'tests_count': len(dictionary),
                    'passed_tests': sum(dictionary.values())}
    else:
        return False
