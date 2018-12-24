from django.urls import path

from nopass import views

urlpatterns = [
    path("create/",views.create_account),
    path("change_email/",views.change_email),
    path("send/",views.send_login),
    path("bad_token/",views.bad_token,name="bad_token"),
    path("<uidb64>/<token>/",views.complete_login,name="nopass_login"),
]