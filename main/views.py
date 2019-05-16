from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.forms.models import model_to_dict
from .forms import NewUserForm, AddCourseForm, AddTaskForm, EditorSubmitForm, UploadCodeForm, SelectLanguageForm, CustomAuthForm, AddTestForm
from .models import Course, Task, Test, Language, User, Statistics

from modules.Tests import testReciever 
from modules.Containers.client import send_request
from datetime import datetime, timedelta
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
        profile_user = request.user
        if request.GET:
            user_id = request.GET['user_id']
            profile_user = User.objects.get(pk=user_id)

        stats = Statistics.objects.filter(user=profile_user)
        today = datetime.now()
        stats = stats.filter(date__range=[today - timedelta(days=60), today])
        
        dates = [today - timedelta(days=x) for x in range(60, -1, -1)]
        extended_stats = []
        for date in dates:
            day_stats = stats.filter(date=date).first()
            extended_stats.append({
                'date': date.strftime('%d %b'), 
                'sends': day_stats.sends if day_stats else 0, 
                'completed_tasks': day_stats.completed_tasks if day_stats else 0,
            })
        
        return render(request=request,
                      template_name='main/profile.html',
                      context={'user': request.user,
                               'profile_user': profile_user,
                               'stats': extended_stats})


def single_slug(request, single_slug):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')

    if request.is_ajax():
        if 'task_id' in request.POST:
            task_id = request.POST['task_id']
            print(f'Удаление задания {task_id}')
            selected_task = Task.objects.get(id=task_id)
            selected_task.delete()
            return HttpResponse()

        course = Course.objects.get(pk=int(single_slug))
        request.user.add_course(course)
        print(f'{request.user} записался на курс {course}')
        return HttpResponse()
    
    course = Course.objects.get(pk=int(single_slug))
    tasks = Task.objects.filter(course__id=course.id).order_by('rating')
    completed_tasks = [t.id for t in request.user.completed_tasks.all()]

    participants_users = User.objects.filter(courses__in=[course])
    return render(request=request,
                  template_name='main/course.html',
                  context={'course': course,
                           'tasks': tasks,
                           'user_courses': request.user.courses.all(),
                           'completed_tasks': completed_tasks,
                           'participants_users': participants_users})


def task_single_slug(request, single_slug, task_single_slug):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')

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

            completed_course = False
            if all(passed.values()):
                request.user.completed_tasks.add(task)
                completed_tasks = request.user.completed_tasks.all().filter(course=course.id)
                course_tasks = Task.objects.filter(course=course.id)

                try:
                    completed_tasks_stats = Statistics.objects.get(date=datetime.now(), user=request.user)
                    completed_tasks_stats.completed_tasks += 1
                except:
                    completed_tasks_stats = Statistics(date=datetime.now(), completed_tasks=1, user=request.user)
                completed_tasks_stats.save()

                if set(completed_tasks) == set(course_tasks):
                    completed_course = request.user.participation_set.get(course_id=course.id)
                    completed_course.completed = True
                    completed_course.save()
                    completed_course = True
                    #TODO Для прохождения курсов?
                    #stats = Statistics.objects.filter(user=request.user)
                    #stats = stats.filter(date=[datetime.now() - timedelta(days=90), datetime.now()])
            
            public_outs = outs[:len(public_tests)]
            public_tests = public_tests.values()
            for test, out in zip(public_tests, public_outs):
                test['result'] = out[0]
                test['error'] = out[1]
            
            try:
                sends_stats = Statistics.objects.get(date=datetime.now(), user=request.user)
                sends_stats.sends += 1
            except:
                sends_stats = Statistics(date=datetime.now(), sends=1, user=request.user)
            sends_stats.save()
            
            return render(request=request,
                          template_name='main/includes/tests.html',
                          context={'tests': public_tests,
                                   'passed': passed,
                                   'completed_course': completed_course})
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


def homepage(request):
    return render(request=request,
                  template_name='main/home.html')


def courses(request):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')

    courses = Course.objects.all()
    if request.is_ajax():
        if 'filters' in request.POST:
            if 'completed_courses' in request.POST:
                completed_courses = bool(request.POST['completed_courses'])
                if completed_courses:
                    user_completed_courses = request.user.participation_set.filter(completed=True)
                    courses = [c.course for c in user_completed_courses]

            if 'enrolled_courses' in request.POST:
                enrolled_courses = bool(request.POST['enrolled_courses'])
                if enrolled_courses:
                    enrolled_courses = [c.id for c in request.user.courses.all()]
                    courses = courses.filter(pk__in=enrolled_courses)

            if 'my_courses' in request.POST:
                my_courses = bool(request.POST['my_courses'])
                if my_courses:
                    courses = courses.filter(author=request.user)
    
            if 'search' in request.POST:
                search = str(request.POST['search'])
                if search:
                    courses = courses.filter(title__contains=search)

            return render(request=request,
                          template_name='main/includes/courses-panel.html',
                          context={'courses': courses,
                                   'user_courses': request.user.courses.all()})


        course_id = request.POST['course_id']
        if 'in_course' in request.POST: 
            in_course = bool(request.POST['in_course'])
            selected_course = Course.objects.get(id=course_id)
            
            if in_course:
                request.user.remove_course(selected_course)
                tasks = request.user.completed_tasks.all().filter(course_id=course_id)
                [request.user.completed_tasks.remove(t) for t in tasks]
                print(f'{request.user} покинул курс {selected_course}')
            else:
                request.user.add_course(selected_course)
                print(f'{request.user} записался на курс {selected_course}')
            
            return HttpResponse()  
        
        else:
            print(f'Удаление курса {course_id}')
            selected_course = Course.objects.get(id=course_id)

            if selected_course.author != request.user and not request.user.is_superuser:
                return redirect('ExamineLab:courses')

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
        form = CustomAuthForm(request, request.POST)
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

    form = CustomAuthForm()
    return render(request,
                  'main/login.html',
                  {'form': form})


def error_404(request):
    return render(request=request,
                  template_name='404.html')


def add_or_edit_course(request):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')
    
    course_id = None
    if request.method == 'POST':
        form = AddCourseForm(request, request.POST)
        title = request.POST['title']
        summary = request.POST['summary']
        
        if request.path == '/add_course/':
            new_course = Course(title=title, summary=summary, author=request.user)
            new_course.save()
            messages.success(request, f'Добавлен новый курс {title}')
            print(f'Добавлен новый курс {title}')

        elif request.path == '/edit_course/':
            course_id = request.GET['course_id']
            selected_course = Course.objects.get(pk=course_id)
            selected_course.title = title
            selected_course.summary = summary
            selected_course.save()
            messages.info(request, f'Обновлён курс {title}')
            print(f'Обновлён курс {title}')
        
        return redirect('ExamineLab:courses')
    
    if request.path == '/add_course/':
        form = AddCourseForm()
        return render(request=request,
                      template_name='main/add_or_edit_course.html',
                      context={'form': form})

    elif request.path == '/edit_course/':
        course_id = request.GET['course_id']
        course = Course.objects.get(pk=course_id)

        if course.author != request.user and not request.user.is_superuser:
            return redirect('ExamineLab:courses')
    
        form = AddCourseForm(initial={'title': course.title,
                                      'summary': course.summary})
        
        return render(request=request,
                      template_name='main/add_or_edit_course.html',
                      context={'form': form,
                               'course': course})


def add_or_edit_task(request):
    if request.user.is_anonymous:
        return redirect('ExamineLab:register')
    
    course_id = request.GET['course_id']
    course = Course.objects.get(pk=course_id)
    if request.method == 'POST':
        if 'rating' in request.POST:
            form = AddTaskForm(request, request.POST)
            title = request.POST['title']
            summary = request.POST['summary']
            rating = request.POST['rating']
            solution = request.POST['solution']
            
            if request.path == '/add_task/':
                new_task = Task(title=title, summary=summary, rating=rating, 
                                    solution=solution, course=course)
                new_task.save()
                messages.success(request, f'Добавлено новое задание {title}')
                print(f'Добавлено новое задание {title}')

            elif request.path == '/edit_task/':
                task_id = request.GET['task_id']
                selected_task = Task.objects.get(pk=task_id)
                selected_task.title = title
                selected_task.summary = summary
                selected_task.rating = rating
                selected_task.solution = solution
                selected_task.save()
                messages.info(request, f'Обновлёно задание {title}')
                print(f'Обновлёно задание {title}')
        
        #else:
        #    form = AddTaskForm(request, request.POST)
        #    title = request.POST['title']
        #    input = request.POST['input']
        #    output = request.POST['output']
        #    #public = request.POST['public']
#
        #    if request.path == '/edit_task/':
        #        new_test = Test(title=title, input=input, output=output, 
        #                        task=task, public=False)
        #        new_test.save()
        #        messages.success(request, f'Добавлен новый тест {title}')
        #        print(f'Добавлен новый тест {title}')
        #    elif request.path == '/edit_task/':
        #        pass

        return redirect(f'../courses/{course.id}')
    
    if request.path == '/add_task/':
        form = AddTaskForm()
        test_form = AddTestForm()
        return render(request=request,
                      template_name='main/add_or_edit_task.html',
                      context={'form': form,
                               'test_form': test_form,
                               'course': course})

    elif request.path == '/edit_task/':
        if course.author != request.user and not request.user.is_superuser:
            return redirect(f'../courses/{course.id}')

        task_id = request.GET['task_id']
        task = Task.objects.get(pk=task_id)
        form = AddTaskForm(initial={'title': task.title,
                                    'summary': task.summary,
                                    'rating': task.rating,
                                    'solution': task.solution})
        #TODO
        test_form = AddTestForm()
        return render(request=request,
                      template_name='main/add_or_edit_task.html',
                      context={'form': form,
                               'test_form': test_form,
                               'course': course,
                               'task': task,
                               'tests': Test.objects.filter(task=task)})


def roles(request):
    if not request.user.is_superuser:
        return redirect('ExamineLab:register')

    if request.is_ajax():
        user_id = request.POST['user_id']
        role = request.POST['role']

        user = User.objects.get(pk=user_id)
        if role == 'is_user':
            user.is_primary_user = True
            user.is_staff = False
            user.is_superuser = False
        elif role == 'is_staff':
            user.is_primary_user = True
            user.is_staff = True
            user.is_superuser = False
        elif role == 'is_superuser':
            user.is_primary_user = True
            user.is_staff = True
            user.is_superuser = True
        user.save()

        return HttpResponse()

    return render(request=request,
                  template_name='main/roles.html',
                  context={'users': User.objects.all()})
