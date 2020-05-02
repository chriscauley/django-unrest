from django.urls import path

from unrest.user import views
from unrest.views import spa

urlpatterns = [
    path('api/auth/user.json', views.user_json),
    path('api/auth/login/', views.login_ajax),
    path('api/auth/signup/', views.signup_ajax),
    path('api/auth/logout/', views.logout_ajax),
    path('reset-password-confirm/<uidb64>/<token>/', spa, name='password_reset_confirm'),
]