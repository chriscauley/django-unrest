import json
import random
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model

# This registers all the form views
from unrest.user.forms import get_reset_user

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

def signup_guest(request):
    if not getattr(settings, 'UNREST_ALLOW_GUEST', False):
        return JsonResponse(status=400)
    User = get_user_model()
    rando = random.randint(0, 100000)
    while User.objects.filter(username=f'guest{rando}'):
        rando = random.randint(0, 100000)
    user = User.objects.create(username=f'guest{rando}')
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({})

user_json.extras = []

def logout_ajax(request):
  logout(request)
  return JsonResponse({})

def password_reset(request, uidb64, token):
    user = get_reset_user(uidb64, token)
    if not user:
        return HttpResponseRedirect("/#/reset-unsuccessful/") # TODO
    request.session['reset-uidb64'] = uidb64
    request.session['reset-token'] = token
    return HttpResponseRedirect('/#/reset/')