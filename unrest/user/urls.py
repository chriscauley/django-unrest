from django.urls import path

from unrest.user import views

urlpatterns = [
    path('user.json', views.user_json),
    path('login/', views.login_ajax),
    path('signup/', views.signup_ajax),
    path('logout/', views.logout_ajax),
]