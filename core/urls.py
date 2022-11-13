from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("settings/", views.settings, name="settings"),
    path("upload/", views.upload, name="upload"),
    path("profile/<str:pk>", views.profile, name="profile"),
    path("follow/", views.follow, name="follow"),
    path("search/", views.search, name="search"),
    path("like-post/", views.like_post, name="like-post"),
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.log_out, name="logout")
]
