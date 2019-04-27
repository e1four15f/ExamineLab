from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


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
        return self.title


class Test(models.Model):
    """Таблица с тестами"""
    title = models.CharField(max_length=title_size)
    input = models.TextField()
    output = models.TextField()

    task = models.ForeignKey(Task, on_delete=models.CASCADE, default=0)

    class Meta:
        verbose_name_plural = 'Tests'

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Таблица с комментариями
    TODO сделать динамическое заполнение таблицы через взаимодействие с пользователем"""
    summary = models.TextField(max_length=summary_size)

    class Meta:
        verbose_name_plural = 'Comments'


class Language(models.Model):
    """Таблица с языками программировани"""
    name = models.CharField(max_length=50, primary_key=True)
    extention = models.CharField(max_length=10)
    launch_command = models.CharField(max_length=50)
    optional = models.CharField(max_length=350,default='rm <path>*')

    class Meta:
        verbose_name_plural = 'Languages'

    def __str__(self):
        return self.name


class Logs(models.Model):
    """Таблица с логами запусков программ пользователей"""
    name = models.ForeignKey(Language, on_delete = models.CASCADE)
    stdout = models.TextField(blank = True)    
    stderr = models.TextField(blank = True)

    class Meta:
        verbose_name_plural = 'Logs'

    def __str__(self):
        return '{}: {} | {}'.format(self.name.name, self.stderr, self.stdout[:20])












