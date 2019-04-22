from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from djangocodemirror.fields import CodeMirrorField


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class SubmitForm(forms.Form):
    submit_solution = CodeMirrorField(label='Ваш код здесь', 
                        config_name='my_mode', required=False)

    class Meta:
        fields = ('code')


class UploadCodeForm(forms.Form):
    widget = forms.ClearableFileInput(attrs={
            'id': 'upload_form',
            'accept': '.py'})

    file = forms.FileField(label='', required=False, widget=widget)