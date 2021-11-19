import random

from django.conf import settings
from django import forms
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

if 'django_registration' in settings.INSTALLED_APPS:
    from django_registration.forms import RegistrationFormUniqueEmail
    from django_registration.backends.activation.views import RegistrationView
    from django_registration import validators
else:
    class RegistrationFormUniqueEmail(forms.ModelForm):
        class Meta:
            pass

from unrest import schema

def get_reset_user(uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        return None

    if default_token_generator.check_token(user, token):
        return user

@schema.register
class PasswordResetForm(PasswordResetForm):
    user_can_POST = 'ANY'
    # the django password reset form uses a bunch of kwargs on save, making it very non-standard
    # we hack them in here so that this plays nice with the rest of the schema form flow
    def save(self, *args, **kwargs):
        kwargs['request'] = self.request
        return super().save(*args, **kwargs)

@schema.register
class SetPasswordForm(SetPasswordForm):
    user_can_POST = 'ANY'
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
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return user

@schema.register
class SignUpForm(RegistrationFormUniqueEmail):
    password1 = forms.CharField(label='Password', max_length=128, widget=forms.PasswordInput)
    user_can_POST = 'ANY'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields.pop('password2')
    def clean(self, *args, **kwargs):
        self.cleaned_data['password2'] = self.cleaned_data.get('password1')
        super().clean()
    class Meta(RegistrationFormUniqueEmail.Meta):
        model = get_user_model()
        fields = ['username', 'email', 'password1']

    def save(self, commit=False):
        user = super().save(commit=False)

        if getattr(settings, 'UNREST_VERIFY_EMAIL', None):
            # use django_registration to send email to user
            user.is_active = False

            view = RegistrationView()
            view.request = self.request
            view.send_activation_email(user)
            user.save()
        else:
            user.save()
            login(self.request,  user, backend='django.contrib.auth.backends.ModelBackend')

        return user


@schema.register
class LoginForm(forms.Form):
    user_can_POST = 'ANY'
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', max_length=128, widget=forms.PasswordInput)
    def clean(self):
        User = get_user_model()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not username and password:
            return self.cleaned_data
        user = User.objects.filter(username=username).first()
        if user:
            if user.check_password(password):
                self.user = user
                return self.cleaned_data
        raise forms.ValidationError("Username and password do not match", code='password_mismatch')
    def save(self, commit=True):
        login(self.request, self.user, backend='django.contrib.auth.backends.ModelBackend')


@schema.register
class UserSettingsForm(forms.ModelForm):
    user_can_GET = 'self'
    user_can_PUT = 'self'
    def clean_username(self):
        value = self.cleaned_data.get('username')
        if value != self.request.user.username:
            error_message = 'Another user has this username.'
            validators.validate_unique(get_user_model(), 'username', error_message)(value)
        validators.ReservedNameValidator()(value)
        return value
    def clean_email(self):
        value = self.cleaned_data.get('email')
        if value != self.request.user.email:
            error_message = 'Another user has this email.'
            validators.validate_unique(get_user_model(), 'email', error_message)(value)
        return value
    class Meta:
        model = get_user_model()
        fields = getattr(settings, 'UNREST_USER_SETTINGS_FIELDS', ['username', 'email'])