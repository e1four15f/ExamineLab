from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user



class SubmitForm(forms.Form):
    widget = forms.Textarea(attrs={'style': 'resize:none; height:50%'})
    submit_solution = forms.CharField(label='Ваш код здесь', widget=widget)

    class Meta:
        fields = ('code')
