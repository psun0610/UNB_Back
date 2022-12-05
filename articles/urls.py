from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register("articles", views.ArticleViewSet, basename="article")
router.register("comment", views.CommentViewSet, basename="comment")
app_name = "articles"

urlpatterns = [
    path("", include(router.urls)),
    path("<int:article_pk>/article_detail/", views.get_article),
    path("<int:game_pk>/game_pick/", views.pick_AB),
    path("new_article", views.today_article),
]
