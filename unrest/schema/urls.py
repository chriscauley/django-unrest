from django.urls import path

from .views import schema_form

urlpatterns = [
    path('api/schema/<form_name>/', schema_form),
]