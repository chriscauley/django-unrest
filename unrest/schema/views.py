from django.http import JsonResponse, Http404
from django.contrib.auth import get_user_model

import json
import re
from ..pagination import paginate
from .utils import form_to_schema, get_default_value

FORMS = {}


def clean_form_name(form_name):
    form_name = form_name
    form_name = re.sub(r'(?<!^)(?=[A-Z])', '-', form_name).lower()
    return re.sub(r'-form$', '', form_name)


def register_admin(admin, form_name=None):
    print(form_name, admin)
    if isinstance(admin, str):
        # register is being used as a decorator and args are curried and reversed
        return lambda actual_admin: register_admin(actual_admin, form_name=admin)
    register(admin.form, form_name)
    return admin


def register(form, form_name=None):
    if isinstance(form, str):
        # register is being used as a decorator and args are curried and reversed
        return lambda actual_form: register(actual_form, form_name=form)
    form_name = clean_form_name(form_name or form.__name__)
    old_form = FORMS.get(form_name, form)
    if repr(form) != repr(old_form):
        e = f"Form with name {form_name} has already been registered.\nOld: {old_form}\nNew:{form}"
        raise ValueError(e)

    FORMS[form_name] = form
    return form


def unregister(form_name):
    FORMS.pop(clean_form_name(form_name), None)


def schema_form(request, form_name, object_id=None, method=None, content_type=None):
    form_name = clean_form_name(form_name)
    if form_name.endswith('-form'):
        raise DeprecationError('Schema forms should no longer end in "Form" or "-form"')
    if not form_name in FORMS:
        raise Http404(f"Form with name {form_name} does not exist")

    method = method or request.method
    content_type = content_type or request.headers.get('Content-Type', None)
    form_class = FORMS[form_name]
    _meta  = getattr(form_class, 'Meta', object())
    kwargs = {}
    print(object_id)
    if object_id and hasattr(_meta, 'model'):
        print('wtf')
        kwargs['instance'] = _meta.model.objects.get(id=object_id)
    if getattr(_meta, 'login_required', None) and not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to do this'}, status=403)

    def check_permission(permission):
        if request.user.is_superuser:
            return True
        instance = kwargs.get('instance')
        f = getattr(form_class, 'user_can_' + permission, None)
        if f == 'SELF':
            return request.user == instance
        if f == 'OWN':
            return request.user == instance.user
        if f == 'ANY':
            return True
        return f and f(instance, request.user)

    if request.method == "POST" or request.method == "PUT":
        # POST/PUT /api/schema/MODEL/ or /api/schema/MODEL/PK/
        if not check_permission('POST'):
            return JsonResponse({'error': 'You cannot edit this resource.'}, status=403)
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
            return JsonResponse(data)
        errors = { k: v[0] for k, v in form.errors.get_json_data().items()}
        return JsonResponse({'errors': errors}, status=400)

    if request.method == "DELETE":
        # DELETE /api/schema/MODEL/ or /api/schema/MODEL/PK/
        if kwargs.get('instance') and check_permission('DELETE'):
            kwargs['instance'].delete()
            return JsonResponse({})
        return JsonResponse({'error': 'You cannot edit this resource.'}, status=403)

    if kwargs.get('instance') and not check_permission('GET'):
        return JsonResponse({'error': 'You do not have access to this resource'}, status=403)

    if request.GET.get('schema'):
        # /api/schema/MODEL/?schema=1 or /api/schema/MODEL/PK/?schema=1
        schema = form_to_schema(form_class(**kwargs))
        return JsonResponse({'schema': schema})

    def process(instance):
        out = { 'id': instance.id }
        form = form_class(instance=instance)
        for field_name in form.fields:
            out[field_name] = get_default_value(form, field_name)
        return out

    if kwargs.get('instance'):
        # /api/schema/MODEL/PK/
        return JsonResponse(process(form_class(**kwargs)))

    # defaults to /api/schema/MODEL/
    if not check_permission('LIST'):
        return JsonResponse({'error': 'You do not have access to this resource'}, status=403)
    model = _meta.model
    if model.__name__ == 'User':
        model = get_user_model()
    query = model.objects.all()
    return JsonResponse(paginate(query, process=process, query_dict=request.GET))



