from .models import *
from django.db import models
from django.contrib import admin
from django.template.defaulttags import register


admin.site.register(Course)
admin.site.register(Task)
admin.site.register(Test)
admin.site.register(User)
admin.site.register(Statistics)
#admin.site.register(PermissionGroup)
#admin.site.register(Permission)
#admin.site.register(UserCourseSpecificPermissions)
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


@register.filter
def get_course_progress(course_id, completed_tasks):
    course_tasks = Task.objects.filter(course=course_id)
    completed_tasks = completed_tasks.filter(course=course_id)

    try:
        percent = len(completed_tasks)/len(course_tasks)*100
    except ZeroDivisionError:
        percent = 100
    
    data = {
        'percents': percent,
        'all': len(course_tasks),
        'completed': len(completed_tasks)
    }
    return data


@register.filter
def get_completed(participation_set, completed):
    return participation_set.filter(completed=completed)


@register.filter
def is_completed(course, user):
    course = user.participation_set.filter(course=course)
    if len(course):
        return course.first().completed
    return False
