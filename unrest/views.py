from django.apps import apps
from django.http import JsonResponse, HttpResponseRedirect


def redirect(request,url=None):
    return HttpResponseRedirect(url)

def list_view(request,app_name,model_name):
    app = apps.get_app_config(app_name)
    model = app.get_model(model_name)
    items = model.objects.request_filter(request)
    return JsonResponse({
        'results': [i.as_json for i in items],
    })

def user_json(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({})
    keys = ['id','username','email']
    return JsonResponse({
        'user': { k: getattr(user,k) for k in keys },
    })