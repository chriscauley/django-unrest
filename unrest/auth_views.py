import json
from django.http import JsonResponse
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


def login_ajax(request):
  data = json.loads(request.body.decode('utf-8') or "{}")
  form = AuthenticationForm(request, data)
  if form.is_valid():
    login(request, form.get_user())
    return JsonResponse({})
  raise NotImplementedError()


def signup_ajax(request):
  data = json.loads(request.body.decode('utf-8') or "{}")
  form = UserCreationForm(data)
  if form.is_valid():
    return JsonResponse({})
  raise NotImplementedError()


def logout_ajax(request):
  logout(request)
  return JsonResponse({})