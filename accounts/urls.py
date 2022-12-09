from django.urls import path, include
from . import views

urlpatterns = [
    path("google/login", views.google_login, name="google_login"),
    path("google/callback/", views.google_callback, name="google_callback"),
    path(
        "google/login/finish/",
        views.GoogleLogin.as_view(),
        name="google_login_todjango",
    ),
    path("kakao/login", views.kakao_login, name="kakao_login"),
    path("kakao/callback/", views.kakao_callback, name="kakao_callback"),
    path(
        "kakao/login/finish/", views.KakaoLogin.as_view(), name="kakao_login_todjango"
    ),
    path("<int:user_pk>/my_page/", views.my_page, name="my_page"),
    path(
        "<int:user_pk>/my_page/<int:userbadge_pk>/",
        views.changebadge,
        name="changebadge",
    ),
]
