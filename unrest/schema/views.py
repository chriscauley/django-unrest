from django.http import JsonResponse, Http404

from .utils import form_to_schema
import json

FORMS = {}


def register(form, form_name=None):
    if isinstance(form, str):
        # register is being used as a decorator and args are curried and reversed
        return lambda actual_form: register(actual_form, form_name=form)
    form_name = form_name or form.__name__
    old_form = FORMS.get(form_name, form)
    if repr(form) != repr(old_form):
        e = f"Form with name {form_name} has already been registered.\nOld: {old_form}\nNew:{form}"
        raise ValueError(e)

    FORMS[form_name] = form
    return form


def schema_form(request, form_name, object_id=None, method=None, content_type=None):
    if not form_name in FORMS:
        raise Http404(f"Form with name {form_name} does not exist")

    method = method or request.method
    content_type = content_type or request.headers.get('Content-Type', None)
    form_class = FORMS[form_name]
    _meta  = getattr(form_class, 'Meta', object())
    kwargs = {}
    if object_id and hasattr(_meta, 'model'):
        kwargs['instance'] = _meta.model.objects.get(id=object_id)
    if getattr(_meta, 'login_required', None) and not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to do this'}, status=403)

    if request.method == "POST":
        if content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8') or "{}")
            form = form_class(data, **kwargs)
        else:
            form = form_class(request.POST, request.FILES, **kwargs)

        form.request = request
        if form.is_valid():
            instance = form.save()
            data = {}
            if instance:
                data = {'id': instance.id, 'name': str(instance)}
            return JsonResponse({ 'schema': form_to_schema(form_class(**kwargs)) })
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)
    schema = form_to_schema(form_class(**kwargs))
    return JsonResponse({'schema': schema})

