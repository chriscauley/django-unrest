from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.static import serve
from django.middleware.csrf import get_token
import json
import subprocess
import os

@ensure_csrf_cookie
def index(request, *args, **kwargs):
    path = kwargs.get('path', finders.find('index.html'))
    response = serve(
        request,
        os.path.basename(path),
        os.path.dirname(path)
    )
    _hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    response.set_cookie("GIT_HASH", _hash.decode('utf-8').strip())
    return response

@ensure_csrf_cookie
def get_csrf(request):
    return HttpResponse(get_token(request))


def spa(request, *args, **kwargs):
    raise Exception('Use index instead of spa')


def favicon(request):
    path = finders.find(getattr(settings,'FAVICON','favicon.ico'))
    if not path:
        return HttpResponse(status=404)
    return serve(
        request,
        os.path.basename(path),
        os.path.dirname(path)
    )

def redirect(request,url=None):
    return HttpResponseRedirect(url)

def superuser_api_view(request, app_name, model_name):
    app = apps.get_app_config(app_name)
    model = app.get_model(model_name)
    data = json.loads(request.body.decode('utf-8') or "{}")
    if not request.method == "POST":
        return list_view(request, app_name, model_name)
    if not request.user.is_superuser:
        raise NotImplementedError("Only superusers can use this view")
    data = json.loads(request.body.decode('utf-8') or "{}")
    id = data.pop("id", 0)
    if id:
        obj = model.objects.get(id=id)
        obj.data = data
        obj.save()
    else:
        obj = model.objects.create(data=data)
    return JsonResponse(obj.as_json)


def list_view(request, app_name, model_name):
    app = apps.get_app_config(app_name)
    model = app.get_model(model_name)
    data = json.loads(request.body.decode('utf-8') or "{}")
    if data:
        id = data.pop("id",None)
        if id:
            obj = model.from_data(data,request=request,id=id)
        else:
            obj = model.from_data(data,request=request)
        obj.save()
        return JsonResponse(obj.as_json)
    items = model.objects.request_filter(request)
    return JsonResponse({
        'results': [i.as_json for i in items],
    })

def intentional_500(request, *args, **kwargs):
    raise Exception("Intentional 500 error")