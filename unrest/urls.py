from django.urls import path

from unrest import views

urlpatterns = [
  path('favicon.ico', views.favicon)
]