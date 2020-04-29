import json
from django.http import JsonResponse, Http404
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm

from unrest.schema import form_to_schema
from .forms import SignupForm, PasswordResetConfirmForm

def form_to_rjsf_response(form):
  if not form.errors:
    return {}
  return {'errors': form.errors.get_json_data()}


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


FORMS = {}


def register(form, form_name=None):
  if isinstance(form, str):
    # register is being used as a decorator and args are curried and reversed
    return lambda actual_form: register(actual_form, form_name=form)
  form_name = form_name or form.__name__
  old_form = FORMS.get(form_name, form)
  if form != old_form:
    raise ValueError(f"Form with name {form_name} has already been registered.\nOld: {old_form}\nNew:{form}")

  FORMS[form_name] = form


register(PasswordResetForm)
register(PasswordChangeForm)
register(PasswordResetConfirmForm)

def schema_form(request, form_name, method=None):
  if not form_name in FORMS:
    raise Http404(f"Form with name {form_name} does not exist")

  method = method or request.method
  form_class = FORMS[form_name]
  if request.method == "POST":
    data = request.POST or json.loads(request.body.decode('utf-8') or "{}")
    form = form_class(data, request.FILES)
    form.request = request
    if form.is_valid():
      instance = form.save()
      data = {}
      if instance:
        data = {'id': instance.id, 'name': str(instance)}
      return JsonResponse(data)
    return JsonResponse(form_to_rjsf_response(form))
  schema = form_to_schema(FORMS[form_name]())
  return JsonResponse({'schema': schema})