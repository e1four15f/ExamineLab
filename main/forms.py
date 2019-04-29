from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from djangocodemirror.fields import CodeMirrorField
from .models import Language


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
