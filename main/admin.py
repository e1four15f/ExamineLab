from django.contrib import admin
from django.db import models
from django.template.defaulttags import register
from .models import *


admin.site.register(Course)
admin.site.register(Task)
admin.site.register(Test)
admin.site.register(User)
#admin.site.register(PermissionGroup)
#admin.site.register(Permission)
#admin.site.register(UserCourseSpecificPermissions)
admin.site.register(Language)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def check_in_course(course, user_courses):
    return course in user_courses


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
