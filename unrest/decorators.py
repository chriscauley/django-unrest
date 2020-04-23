import functools

from django.http import JsonResponse


def login_required(func):
  @functools.wraps(func)
  def wrapped(request, *args, **kwargs):
    if request.user.is_authenticated:
      return func(request, *args, **kwargs)
    return JsonResponse({}, status_code=403)
  return wrapped