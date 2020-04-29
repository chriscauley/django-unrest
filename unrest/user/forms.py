from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import is_safe_url, urlsafe_base64_decode


class SignupForm(forms.ModelForm):
  class Meta:
    model = get_user_model()
    fields = ('username', 'password')


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
