from django.http import JsonResponse

from .utils import form_to_schema


FORMS = {}

def FormResponse(form):
    if not form.errors:
        return JsonResponse({})
    return JsonResponse({'errors': form.errors.get_json_data()})


def register(form, form_name=None):
    if isinstance(form, str):
        # register is being used as a decorator and args are curried and reversed
        return lambda actual_form: register(actual_form, form_name=form)
    form_name = form_name or form.__name__
    old_form = FORMS.get(form_name, form)
    if form != old_form:
        e = f"Form with name {form_name} has already been registered.\nOld: {old_form}\nNew:{form}"
        raise ValueError(e)

    FORMS[form_name] = form


def schema_form(request, form_name, method=None):
    if not form_name in FORMS:
        raise Http404(f"Form with name {form_name} does not exist")

    method = method or request.method
    form_class = FORMS[form_name]
    if request.method == "POST":
        # TODO handle form data differently by content type
        data = request.POST or json.loads(request.body.decode('utf-8') or "{}")
        form = form_class(data, request.FILES)
        form.request = request
        if form.is_valid():
            instance = form.save()
            data = {}
            if instance:
                data = {'id': instance.id, 'name': str(instance)}
            return JsonResponse(data)
        return FormResponse(form)
    schema = form_to_schema(FORMS[form_name]())
    return JsonResponse({'schema': schema})

