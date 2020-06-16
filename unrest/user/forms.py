from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm, PasswordResetForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import is_safe_url, urlsafe_base64_decode
from unrest import schema


schema.register(PasswordChangeForm)


@schema.register
class LoginForm(AuthenticationForm):
  def __init__(self, *args, **kwargs):
    # Authentication uses request as an argument, unrest sets self.request after initialization
    return super().__init__(None, *args, **kwargs)
  def save(self):
    login(self.request, self.user_cache)
    return self.user_cache

@schema.register
class PasswordResetForm(PasswordResetForm):
  form_title = 'Forgot Password'


@schema.register
class SignupForm(forms.ModelForm):
  def clean_email(self):
    email = self.cleaned_data.get('email', '')
    exists = get_user_model().objects.filter(username__iexact=email)
    exists = exists or get_user_model().objects.filter(email__iexact=email)
    if exists:
      e = "A user with that email already exists. Please use login or password recovery below."
      raise forms.ValidationError(e)
    return email
  def save(self, commit=True):
    user = super().save(commit=commit)
    user.set_password(self.cleaned_data['password'])
    user.username = self.cleaned_data['email']
    if commit:
      user.save()
      login(self.request, user)
    return user
  class Meta:
    model = get_user_model()
    fields = ('email', 'password')


@schema.register
class PasswordResetConfirmForm(SetPasswordForm):
  token = forms.CharField(widget=forms.HiddenInput())
  uidb64 = forms.CharField(widget=forms.HiddenInput())

  def __init__(self, *args, **kwargs):
    # Setpassword deviates from usual Forms by having user as first argument. This undoes that
    super().__init__(None, *args, **kwargs)

  def clean(self):
    data = self.cleaned_data
    UserModel = get_user_model()

    try:
      uid = urlsafe_base64_decode(data['uidb64']).decode()
      self.user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
      raise forms.ValidationError("The password reset link you are using is invalid.")

    if not default_token_generator.check_token(self.user, data['token']):
      raise forms.ValidationError("The password reset link you are using is expired.")
    return data

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    login(self.request, self.user)
