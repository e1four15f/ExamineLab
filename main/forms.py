from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from .models import User
from djangocodemirror.fields import CodeMirrorField



class NewUserForm(UserCreationForm):
    name = forms.CharField(max_length=50, required=False,
                                label='Имя')
    surname = forms.CharField(max_length=50, required=False, 
                                label='Фамилия')
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput,
        help_text='\
        1) Ваш пароль не может быть слишком похож на другую вашу личную информацию.<br/>\
        2) Ваш пароль должен содержать не менее 8 символов.<br/>\
        3) Ваш пароль не может быть часто используемым паролем.<br/>\
        4) Ваш пароль не может быть полностью цифровым.',
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        strip=False,
        help_text='Повторите свой пароль'
    )
    
    class Meta:
        model = User
        fields = ('name', 'surname', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.username = self.cleaned_data['email']
        #user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class SubmitForm(forms.Form):
    submit_solution = CodeMirrorField(label='Ваш код здесь',
                        config_name='my_mode', required=False)

    class Meta:
        fields = ('code')


class AddCourseForm(forms.Form):
    # TODO получать поля из бд
    title_size = 50
    summary_size = 400
    title = forms.CharField(max_length=title_size, required=True,
                                label='Название')
    summary = forms.CharField(max_length=summary_size,
                                label='Описание')

    class Meta:
        fields = ('title', 'summary')


class AddTaskForm(forms.Form):
    # TODO получать поля из бд
    title_size = 50
    summary_size = 400
    title = forms.CharField(max_length=title_size, required=True, 
                                label='Название')
    summary = forms.CharField(max_length=summary_size,
                                label='Описание')
    # TODO Поля для добавление Test-ов
    #rating = forms.Ch

    class Meta:
        fields = ('title', 'summary', 'rating')