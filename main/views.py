from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Course, Task, Test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm, SubmitForm

from modules.Tests import testReciever 
import os

def single_slug(request, single_slug):
    try:
        course = Course.objects.get(pk=int(single_slug))
        tasks = Task.objects.filter(course__id=course.id).order_by('title')
        return render(request=request,
                      template_name='main/course.html',
                      context={'course': course,
                               'tasks': tasks})

    except Course.DoesNotExist:
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

    except Task.DoesNotExist:
        return HttpResponse('404 Task {} not found!'.format(task_single_slug))


def homepage(request):
    return render(request=request,
                  template_name='main/home.html')


def courses(request):
    return render(request=request,
                  template_name='main/courses.html',
                  context={'courses': Course.objects.all})


def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
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
