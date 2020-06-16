import json
from django.http import JsonResponse
from django.contrib.auth import logout

# This registers all the form views
import unrest.user.forms # noqa

def user_json(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({})
    keys = ['id', 'username', 'email', 'is_superuser', 'is_staff']
    data = { k: getattr(user,k) for k in keys }
    if hasattr(user_json, 'get_extra'):
        data.update(user_json.get_extra(user))
    for func in user_json.extras:
        data.update(func(request))
    return JsonResponse({ 'user': data })

user_json.extras = []

def logout_ajax(request):
  logout(request)
  return JsonResponse({})
