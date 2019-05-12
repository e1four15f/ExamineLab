from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

import datetime

title_size = 50
summary_size = 400


class Course(models.Model):
    """Таблица с курсами"""
    title = models.CharField(max_length=title_size)
    summary = models.TextField(max_length=summary_size, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.title


class Task(models.Model):
    """Таблица с заданиями"""
    title = models.CharField(max_length=title_size)
    summary = models.TextField(max_length=summary_size, null=True, blank=True)
    rating = models.SmallIntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)], default=0)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=0)
    solution = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.course.title + ": " + self.title


class Test(models.Model):
    """Таблица с тестами"""
    title = models.CharField(max_length=title_size, null=True, blank=True)
    input = models.TextField()
    output = models.TextField()

    public = models.BooleanField(default=False)

    task = models.ForeignKey(Task, on_delete=models.CASCADE, default=0)

    class Meta:
        verbose_name_plural = 'Tests'

    def __str__(self):
        return self.task.title + ": " + (self.title if self.title else 'Unknown')


#class Permission(models.Model):
#    name = models.CharField(max_length=20)
#    description = models.CharField(max_length=40)


#class PermissionGroup(models.Model):
#    name = models.CharField(max_length=40, primary_key=True)
#    description = models.CharField(max_length=400)
#    permissions = models.ManyToManyField(Permission)


class User(AbstractUser):
    name = models.CharField(max_length=40, null=True, blank=True)
    surname = models.CharField(max_length=40, null=True, blank=True)
    email = models.CharField(max_length=40, primary_key=True)
    #global_permission_groups = models.ManyToManyField(PermissionGroup)
    courses = models.ManyToManyField(Course, through='UserCourseParticipation')
    avatar = models.ImageField(null=True)
    USERNAME_FIELD = 'email'
    objects = UserManager()
    REQUIRED_FIELDS = []

    #def has_permission_group(self, permission_group, course=None):
    #    if course is None:
    #        return len(self.global_permission_groups.all().get(name=permission_group)) == 1
#
    #def add_permission_group(self, permission_group, course=None):
    #    if course is None:
    #        self.global_permission_groups.add(permission_group)
#
    #def remove_permission_group(self, permission_group, course=None):
    #    if course is None:
    #        self.global_permission_groups.remove(permission_group)
#
    #def has_permission(self, permission_id_list, course=None):
    #    if course is None:
    #        return not Permission.objects.filter(models.Q(id__in=permission_id_list) & ~models.Q(permissiongroup__in=self.global_permission_groups.all())).exists()

    def add_course(self, course, date=None):
        self.courses.add(course, through_defaults={'date_joined': datetime.date.today()})

    def remove_course(self, course):
        self.courses.remove(course)

    def __str__(self):
        return email

        
class Language(models.Model):
    """Таблица с языками программировани"""
    name = models.CharField(max_length=50, primary_key=True)
    extention = models.CharField(max_length=10)
    launch_command_linux = models.CharField(max_length=550)
    optional_linux = models.CharField(max_length=351,default='rm <path>*')

    input_help = models.TextField(max_length=550, default='')
    output_help = models.TextField(max_length=550, default='')
    
    class Meta:
        verbose_name_plural = 'Languages'

    def __str__(self):
        return self.name
#
#class UserCourseSpecificPermissions(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    permission = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE)
#    course = models.ForeignKey(Course, on_delete=models.CASCADE)
#

class UserCourseParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_joined = models.DateField()
