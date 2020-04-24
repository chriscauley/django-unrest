import json
from django.http import JsonResponse
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm

from unrest.auth_forms import SignupForm

def form_to_rjsf_response(form):
  if not form.errors:
    return {}
  return {'errors': form.errors.get_json_data()}


def login_ajax(request):
  data = json.loads(request.body.decode('utf-8') or "{}")
  form = AuthenticationForm(request, data)
  if form.is_valid():
    login(request, form.get_user())
  return JsonResponse(form_to_rjsf_response(form))


def signup_ajax(request):
  data = json.loads(request.body.decode('utf-8') or "{}")
  form = SignupForm(data)
  if form.is_valid():
    user = form.save()
    login(request, user)
  return JsonResponse(form_to_rjsf_response(form))


def logout_ajax(request):
  logout(request)
  return JsonResponse({})