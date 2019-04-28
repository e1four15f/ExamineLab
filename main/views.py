from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Course, Task, Test, Language, Logs
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm, SubmitForm, UploadCodeForm

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
            submit_form = SubmitForm(request.POST)
            upload_code_form = UploadCodeForm(request.POST, request.FILES)
            
            if submit_form.is_valid():
                # type(uploaded_code) = <class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
                uploaded_code = request.FILES.get('file') 
                # .py .cpp .java etc
                names = {'.c':'C', '.py': 'Python'}
                lname = names[request.POST['language']]
                selected_language = Language.objects.get(pk=lname)
                submited_solution = submit_form.data['submit_solution']


                user_code = uploaded_code.read() if uploaded_code != None else submited_solution

                try:
                    user_code = user_code.decode('ascii')
                except AttributeError:
                    pass

                passed, outs = testReciever.perform_testing_from_text(user_code, tests, selected_language)

                Logs(name = selected_language, stdout = outs[0][0], stderr = outs[0][1]).save()

                return render(request=request,
                      template_name='main/task.html',
                      context={'languages': Language.objects.all(),
                               'course': course,
                               'task': task,
                               'submit_form': submit_form,
                               'upload_code_form': upload_code_form,
                               'tests': tests,
                               'passed': passed,
                               'error': outs[0][1]})

        else:
            submit_form = SubmitForm()
            upload_code_form = UploadCodeForm()

        return render(request=request,
                      template_name='main/task.html',
                      context={'languages': Language.objects.all(),
                               'course': course,
                               'task': task,
                               'submit_form': submit_form,
                               'upload_code_form': upload_code_form,
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
