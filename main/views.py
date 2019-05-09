from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from .models import Course, Task, Test, Language
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm, EditorSubmitForm, UploadCodeForm, SelectLanguageForm
from django.forms.models import model_to_dict

from modules.Tests import testReciever 
from modules.Containers.client import send_request
import os

def handler404(request, exception, template_name="404.html"):
    response = render_to_response("main/404/404.html")
    response.status_code = 404
    return response


def single_slug(request, single_slug):
    try:
        course = Course.objects.get(pk=int(single_slug))
        tasks = Task.objects.filter(course__id=course.id).order_by('rating')
        return render(request=request,
                      template_name='main/course.html',
                      context={'course': course,
                               'tasks': tasks})

    except Course.DoesNotExist:
        return handler404(request, Course.DoesNotExist)#HttpResponse('404 Course {} not found!'.format(single_slug))


def task_single_slug(request, single_slug, task_single_slug):
    try:
        course = Course.objects.get(pk=int(single_slug))
        task = Task.objects.get(pk=int(task_single_slug))
        tests = Test.objects.filter(task__id=task.id).order_by('-public')
        public_tests = tests.filter(public=True)

        if request.is_ajax():
            selected_language = request.POST['language']
            if 'solution' in request.POST:
                editor_submit_form = EditorSubmitForm(request.POST)
                upload_code_form = UploadCodeForm(request.POST, request.FILES)
                select_language_form = SelectLanguageForm(request.POST)
                
                uploaded_code = request.FILES.get('file') 
                submited_solution = editor_submit_form.data['solution']

                user_code = uploaded_code.read() if uploaded_code != None else submited_solution

                try:
                    user_code = user_code.decode('ascii')
                except AttributeError:
                    pass
                
                data = {
                    'user_code': user_code,
                    'tests': [t for t in tests.values()],
                    'language': model_to_dict(Language.objects.get(pk=selected_language))
                }
                passed, outs = send_request(data)
                
                public_outs = outs[:len(public_tests)]
                public_tests = public_tests.values()
                for test, out in zip(public_tests, public_outs):
                    test['result'] = out[0]
                    test['error'] = out[1]
                
                return render(request=request,
                        template_name='main/includes/tests.html',
                        context={'tests': public_tests,
                                 'passed': passed})
            else:
                editor_submit_form = EditorSubmitForm()
                return render(request=request,
                        template_name='main/includes/editor.html',
                        context={'editor_submit_form': editor_submit_form,
                                 'language': selected_language.lower()})
            
        else:
            editor_submit_form = EditorSubmitForm()
            upload_code_form = UploadCodeForm()
            select_language_form = SelectLanguageForm()

        return render(request=request,
                      template_name='main/task.html',
                      context={'languages': Language.objects.all(),
                               'course': course,
                               'task': task,
                               'editor_submit_form': editor_submit_form,
                               'upload_code_form': upload_code_form,
                               'select_language_form': select_language_form,
                               'tests': public_tests})

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
