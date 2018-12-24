from django.apps import apps
from django.http import JsonResponse


def list_view(request,app_name,model_name):
  app = apps.get_app_config(app_name)
  model = app.get_model(model_name)
  items = model.objects.request_filter(request)
  return JsonResponse({
    'results': [i.as_json for i in items],
  })
