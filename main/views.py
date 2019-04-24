from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
from .models import Course, Task, Test, PermissionGroup, Permission
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm, SubmitForm
from django.views.decorators.csrf import csrf_exempt

from modules.Tests import testReciever 
import os


def test(request):
    print(request.user.email)

    per1,created = Permission.objects.get_or_create(name='1', description='Open')
    print(created)
    per2,created = Permission.objects.get_or_create(name='2', description='Close')
    print(created)
    per1.save()
    per2.save()
    pg,created = PermissionGroup.objects.get_or_create(name='pg1', description='pg1')
    print(pg)
    pg.permissions.add(per1)
    pg.permissions.add(per2)
    pg.save()
    per1, created = Course.objects.get_or_create(title='C++', summary='C++ Course')
    per2, created = Course.objects.get_or_create(title='Java', summary='Java Course')
    per1.save()
    per2.save()
    request.user.add_permission_group(pg)
    request.user.add_course(per1)
    request.user.add_course(per2)
    request.user.save()
    print(request.user.global_permission_groups.last().permissions.all())
    print(request.user.has_permission(permission_id_list=[2]))
    print(request.user.get_courses(1,1))


    return HttpResponse()

def profile(request):
    if request.user.is_anonymous:
        return HttpResponseNotFound()
    return render(request=request,
                  template_name='main/profile.html',
                  context={'user': request.user})

@csrf_exempt
def course_participation_management(request):
    if request.user is None or request.user.is_anonymous:
        return HttpResponseForbidden()
    elif 'course_id' not in request.POST or 'action' not in request.POST:
        print(request.body)
        return HttpResponseBadRequest()
    else:
        try:
            course = Course.objects.get(pk=int(request.POST['course_id']))
            if request.POST['action'] == 'enroll':
                request.user.add_course(course)
                request.user.save()
                return HttpResponse()
            else:
                request.user.remove_course(course)
                return HttpResponse()
        except:
            return HttpResponseBadRequest()

def single_slug(request, single_slug):
    try:
        course = Course.objects.get(pk=int(single_slug))
        tasks = Task.objects.filter(course__id=course.id).order_by('title')
        return render(request=request,
                      template_name='main/course.html',
                      context={'course': course,
                               'tasks': tasks})

    except:
        return HttpResponse('404 Course {} not found!'.format(single_slug))


def task_single_slug(request, single_slug, task_single_slug):
    try:
        course = Course.objects.get(pk=int(single_slug))
        task = Task.objects.get(pk=int(task_single_slug))
        tests = Test.objects.filter(task__id=task.id).order_by('title')

        if request.method == 'POST':
            form = SubmitForm(request.POST)

            if form.is_valid():
                test_checker = testReciever.TestReciever('python3')
                
                #tests_paths = [os.path.abspath('./temp/tests/'+p) for p in os.listdir('./temp/tests')]
                #print(tests_paths)
                user_code_hash = 'program' + str(hash(form.data['submit_solution'])) + '.py'
                with open(user_code_hash,'w') as user_pr:
                    user_pr.write(form.data['submit_solution'])
                passed = test_checker.perform_testing(user_code_hash, tests)
                os.remove(user_code_hash)
                return render(request=request,
                      template_name='main/task.html',
                      context={'course': course,
                               'task': task,
                               'form': form,
                               'tests': tests,
                               'passed': passed})
        else:
            form = SubmitForm()

        return render(request=request,
                      template_name='main/task.html',
                      context={'course': course,
                               'task': task,
                               'form': form,
                               'tests': tests})

    except:
        return HttpResponse('404 Task {} not found!'.format(task_single_slug))


def homepage(request):
    return render(request=request,
                  template_name='main/home.html')


def courses(request):
    #Временное решение!
    courses_attended = request.user.courses.all()
    courses_other = Course.objects.difference(courses_attended)
    return render(request=request,
                  template_name='main/courses.html',
                  context={'courses_attended': courses_attended, 'courses_other': courses_other})


def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('email')
            messages.success(request, 'New Account Created: {}'.format(username))
            login(request, user)
            messages.info(request, 'You are now logged in as: {}'.format(username))
            return redirect('main:homepage')
        else:
            for msg in form.error_messages:
                messages.error(request, '{}: {}'.format(msg, form.error_messages[msg]))

    form = NewUserForm
    return render(request=request,
                  template_name='main/register.html',
                  context={'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('main:homepage')


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, 'You are now logged in as: {}'.format(username))
                return redirect('main:homepage')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')

    form = AuthenticationForm()
    return render(request,
                  'main/login.html',
                  {'form': form})
