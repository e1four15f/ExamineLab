from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

title_size = 50
summary_size = 400


# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=title_size)
    summary = models.TextField(max_length=summary_size, null=True)

    class Meta:
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=title_size)
    summary = models.TextField(max_length=summary_size, null=True)
    rating = models.SmallIntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)], default=0)

    class Meta:
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title


class Test(models.Model):
    title = models.CharField(max_length=title_size)
    input = models.TextField()
    output = models.TextField()

    class Meta:
        verbose_name_plural = 'Tests'

    def __str__(self):
        return self.title


class Comment(models.Model):
    #id = models.AutoField(primary_key=True)
    summary = models.TextField(max_length=summary_size)
    #user_id = models.ForeignKey(User, verbose_name='User', on_delete=models.SET_DEFAULT)

    class Meta:
        verbose_name_plural = 'Comments'

    #def __str__(self):
    #   return self.id


# Связующие таблицы
class CourseTask(models.Model):
    task_id = models.ForeignKey(Task, verbose_name='Task')
    course_id = models.ForeignKey(Course, verbose_name='Course')

    class Meta:
        verbose_name_plural = 'CourseTasks'

    def __str__(self):
        return self.task_id + ' ' +  self.course_id


