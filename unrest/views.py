from django.apps import apps
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
import json
import subprocess

@ensure_csrf_cookie
def index(request, path='dist/index.html'):
    f = open(path,'r')
    response = HttpResponse(f.read())
    _hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    response.set_cookie("GIT_HASH", _hash.decode('utf-8').strip())
    return response

def redirect(request,url=None):
    return HttpResponseRedirect(url)

def superuser_api_view(request,app_name,model_name):
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


def list_view(request,app_name,model_name):
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

def user_json(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({})
    keys = ['id','username','email','is_superuser','is_staff']
    return JsonResponse({
        'user': { k: getattr(user,k) for k in keys },
    })