from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from djangocodemirror.fields import CodeMirrorField



class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

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
    title_size = 50
    summary_size = 400
    title = forms.CharField(max_length=title_size, required=True)
    summary = forms.CharField(max_length=summary_size)

    class Meta:
        fields = ('title', 'summary')


class AddTaskForm(forms.Form):
    title_size = 50
    summary_size = 400
    title = forms.CharField(max_length=title_size, required=True)
    summary = forms.CharField(max_length=summary_size)
    #rating = forms.Ch

    class Meta:
        fields = ('title', 'summary', 'rating')