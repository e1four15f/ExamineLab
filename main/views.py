from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.forms.models import model_to_dict
from .forms import NewUserForm, AddCourseForm, AddTaskForm, EditorSubmitForm, UploadCodeForm, SelectLanguageForm
from .models import Course, Task, Test, Language

from modules.Tests import testReciever 
from modules.Containers.client import send_request
import os


def profile(request):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')

    if request.is_ajax():
        image = request.FILES.get('avatar')
        # TODO Сохраняет локально, а не в бд
        request.user.avatar.save(image.name, image)
        return HttpResponse()
    else:
        return render(request=request,
                    template_name='main/profile.html',
                    context={'user': request.user})


def single_slug(request, single_slug):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')

    if request.is_ajax():
        course = Course.objects.get(pk=int(single_slug))
        request.user.add_course(course)
        print(f'{request.user} записался на курс {course}')
        return HttpResponse()
    else:
        try:
            course = Course.objects.get(pk=int(single_slug))
            tasks = Task.objects.filter(course__id=course.id).order_by('rating')

            return render(request=request,
                        template_name='main/course.html',
                        context={'course': course,
                                'tasks': tasks,
                                'user_courses': request.user.courses.all()})
        except:
            return HttpResponseNotFound()


def task_single_slug(request, single_slug, task_single_slug):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')

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

    except Exception as e:
        print(e)
        return HttpResponseNotFound()


def homepage(request):
    return render(request=request,
                  template_name='main/home.html')


def courses(request):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')

    courses = Course.objects.all()
    if request.user.is_anonymous:
        return register(request)
    
    if request.is_ajax():
        course_id = request.POST['course_id']

        if 'in_course' in request.POST: 
            in_course = bool(request.POST['in_course'])
            selected_course = Course.objects.get(id=course_id)
            
            if in_course:
                request.user.remove_course(selected_course)
                print(f'{request.user} покинул курс {selected_course}')
            else:
                request.user.add_course(selected_course)
                print(f'{request.user} записался на курс {selected_course}')
            
            return HttpResponse()  
        
        else:
            print(f'Удаление курса {course_id}')
            #TODO Проверить не остаётся ли после удаление лишний мусор
            selected_course = Course.objects.get(id=course_id)
            selected_course.delete()
            return HttpResponse()  


    return render(request=request,
                  template_name='main/courses.html',
                  context={'courses': courses, 
                           'user_courses': request.user.courses.all()})


def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('email')
            messages.success(request, f'Создан новый аккаунт {username}')
            login(request, user)
            messages.info(request, f'Добро пожаловать, {username}')
            return redirect('ExamineLab:courses')
        else:
            for msg in form.error_messages:
                messages.error(request, f'{msg}: {form.error_messages[msg]}')

    form = NewUserForm
    return render(request=request,
                  template_name='main/register.html',
                  context={'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('ExamineLab:homepage')


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Добро пожаловать, {username}')
                return redirect('ExamineLab:courses')
            else:
                messages.error(request, 'Неверный email или пароль')
        else:
            messages.error(request, 'Неверный email или пароль')

    form = AuthenticationForm()
    return render(request,
                  'main/login.html',
                  {'form': form})


def error_404(request):
    return render(request=request,
                  template_name='main/404.html')


def add_or_edit_course(request):
    if request.user.is_superuser:
        course_id = None
        if request.method == 'POST':
            form = AddCourseForm(request, request.POST)
            title = request.POST['title']
            summary = request.POST['summary']
            
            if request.path == '/add_course':
                new_course = Course(title=title, summary=summary)
                new_course.save()
                messages.success(request, f'Добавлен новый курс {title}')
                print(f'Добавлен новый курс {title}')
            elif request.path == '/edit_course':
                course_id = request.GET['course_id']
                selected_course = Course.objects.get(pk=course_id)
                selected_course.title = title
                selected_course.summary = summary
                selected_course.save()
                messages.info(request, f'Обновлён курс {title}')
                print(f'Обновлён курс {title}')
            
            return redirect('ExamineLab:courses')

        if request.path == '/add_course':
            form = AddCourseForm()
            return render(request=request,
                          template_name='main/add_or_edit_course.html',
                          context={'form': form})

        elif request.path == '/edit_course':
            try:
                course_id = request.GET['course_id']
                course = Course.objects.get(pk=course_id)
            except:
                return HttpResponseNotFound()

            form = AddCourseForm(initial={'title': course.title,
                                          'summary': course.summary})
            
            return render(request=request,
                          template_name='main/add_or_edit_course.html',
                          context={'form': form,
                                   'course': course})

    return HttpResponseNotFound()


def add_task(request):
    try:
        course_id = request.GET['course_id']
        course = Course.objects.get(pk=course_id)
    except:
        return HttpResponseNotFound()

    if request.user.is_superuser:
        if request.method == 'POST':
            form = AddTaskForm(request, request.POST)
            # TODO добавить в бд
            pass

        form = AddTaskForm()
        return render(request=request,
                      template_name='main/add_task.html',
                      context={'course': course,
                               'form': form})

    return HttpResponseNotFound()


