import random

from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

from server.api.auth import get_reset_user
from server.user.models import User
from server import schema

@schema.register
class PasswordResetForm(PasswordResetForm):
    # the django password reset form uses a bunch of kwargs on save, making it very non-standard
    # we hack them in here so that this plays nice with the rest of the schema form flow
    def save(self, *args, **kwargs):
        kwargs['request'] = self.request
        return super().save(*args, **kwargs)

@schema.register
class SetPasswordForm(SetPasswordForm):
    # In django, token validation is done in the view and user is passed into the form
    # this does all that in clean instead to make it fit into schema form flow
    def __init__(self, *args, **kwargs):
        super().__init__(None, *args, **kwargs)
        del self.fields['new_password1'].help_text

    def clean(self):
        uidb64 = self.request.session.get('reset-uidb64', '')
        token = self.request.session.get('reset-token', '')
        self.user = get_reset_user(uidb64, token)
        if not self.user:
            raise forms.ValidationError('This password reset token has expired')
        return self.cleaned_data

    def save(self, commit=True):
        # password reset token is invalid after save. Remove from session
        user = super().save(commit)
        self.request.session.pop('reset-uidb64', None)
        self.request.session.pop('reset-token', None)
        login(self.request, user)
        return user

def validate_unique(attribute, value, exclude={}):
    users = User.objects.filter(**{attribute: value})
    if exclude:
        users = users.exclude(**exclude)
    user = users.first()
    if user:
        raise forms.ValidationError(f'A user with this {attribute} already exists.')

@schema.register
class SignUpForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['username'].help_text
        self.fields['email'].required = True
    def clean_username(self):
        username = self.cleaned_data['username']
        validate_unique('username', username)
        return username
    def clean_email(self):
        email = self.cleaned_data['email']
        validate_unique('email', email)
        return email
    def save(self, commit=True):
        user = super().save(commit)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        login(self.request,  user)
        return user
    class Meta:
        fields = ('username', 'email', 'password')
        model = User

@schema.register
class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', max_length=128, widget=forms.PasswordInput)
    def clean(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).first()
        if user:
            if user.check_password(self.cleaned_data['password']):
                self.user = user
                return self.cleaned_data
        raise forms.ValidationError("Username and password do not match")
    def save(self, commit=True):
        login(self.request, self.user)
