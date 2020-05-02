import json
from django.http import JsonResponse, Http404
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm

from unrest import schema
from .forms import SignupForm, PasswordResetConfirmForm

def user_json(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({})
    keys = ['id', 'username', 'email', 'is_superuser', 'is_staff']
    data = { k: getattr(user,k) for k in keys }
    if hasattr(user_json, 'get_extra'):
        data.update(user_json.get_extra(user))
    return JsonResponse({ 'user': data })

def login_ajax(request):
  data = json.loads(request.body.decode('utf-8') or "{}")
  data['username'] = data['email']
  form = AuthenticationForm(request, data)
  if form.is_valid():
    login(request, form.get_user())
  return schema.FormResponse(form)


def signup_ajax(request):
  data = json.loads(request.body.decode('utf-8') or "{}")
  form = SignupForm(data)
  if form.is_valid():
    user = form.save()
    login(request, user)
  return schema.FormResponse(form)


def logout_ajax(request):
  logout(request)
  return JsonResponse({})


schema.register(PasswordResetForm)
schema.register(PasswordChangeForm)
schema.register(PasswordResetConfirmForm)
