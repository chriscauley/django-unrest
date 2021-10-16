from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import ModelChoiceIteratorValue
from django.http import JsonResponse as _JsonResponse

class JsonEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, ModelChoiceIteratorValue):
            return obj.value
        return super().default(obj)

def JsonResponse(*args, **kwargs):
    kwargs['encoder'] = JsonEncoder
    return _JsonResponse(*args, **kwargs)