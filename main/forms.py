from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from djangocodemirror.fields import CodeMirrorField
from .models import User, Language, title_size, summary_size


class NewUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=False,
                                label='Имя')
    last_name = forms.CharField(max_length=50, required=False, 
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
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class AddCourseForm(forms.Form):
    title = forms.CharField(max_length=title_size, required=True,
                                label='Название')
    summary = forms.CharField(max_length=summary_size, widget=forms.Textarea({'style': 'resize: vertical;'}),
                                label='Описание')

    class Meta:
        fields = ('title', 'summary')


class AddTaskForm(forms.Form):
    title = forms.CharField(max_length=title_size, required=True, 
                                label='Название')
    summary = forms.CharField(max_length=summary_size, widget=forms.Textarea({'style': 'resize: vertical;'}),
                                label='Описание')
    # TODO Поля для добавление Test-ов
    #rating = forms.Ch

    class Meta:
        fields = ('title', 'summary', 'rating')


class EditorSubmitForm(forms.Form):
    solution = CodeMirrorField(label='Ваш код здесь', 
                        config_name='config', 
                        required=False)


class UploadCodeForm(forms.Form):
    widget = forms.ClearableFileInput(attrs={
            'id': 'upload_form',
            'accept': '.py'})

    file = forms.FileField(label='', required=False, widget=widget)


class SelectLanguageForm(forms.Form):
    language = Language.objects.all()
    choices = ((lang.extention, lang.name) for lang in language)

    widget = forms.Select(attrs={
        'onchange': "$('#upload_form').attr('accept', this.value);\
                     $('#select-language-form').submit()",
        'id': 'id_language'})

    status = forms.ChoiceField(label='', choices=choices, 
                                widget=widget, required=False)
