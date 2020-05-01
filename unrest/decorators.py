import functools

from django.http import JsonResponse


def login_required(func):
  @functools.wraps(func)
  def wrapped(request, *args, **kwargs):
    if request.user.is_authenticated:
      return func(request, *args, **kwargs)
    return JsonResponse({}, status_code=403)
  return wrapped

def cached_method(target):
  def wrapper(*args, **kwargs):
    obj = args[0]
    name = '___' + target.__name__

    if not hasattr(obj, name):
      value = target(*args, **kwargs)
      setattr(obj, name, value)

    return getattr(obj, name)

  return wrapper

def cached_property(target):
  return property(cached_method(target))
