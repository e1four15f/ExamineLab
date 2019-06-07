"""ExamineLab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import path


app_name = 'ExamineLab'

#handler404 = 'ExamineLab.views.handler404'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
    path('courses/', views.courses, name='courses'),
    path('add_course/', views.add_or_edit_course, name='add_or_edit_course'),
    path('edit_course/', views.add_or_edit_course, name='add_or_edit_course'),
    path('courses/<single_slug>', views.single_slug, name='single_slug'),
    path('add_task/', views.add_or_edit_task, name='add_or_edit_task'),
    path('edit_task/', views.add_or_edit_task, name='add_or_edit_task'),
    path('courses/<single_slug>/<task_single_slug>', views.task_single_slug, name='task_single_slug'),
    path('profile/', views.profile, name='profile'),
    path('roles/', views.roles, name='roles'),
    
    path('404', views.error_404, name='404'),
]
