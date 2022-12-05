from django.urls import path, include
from rest_framework import routers
from . import views
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register("articles", views.ArticleViewSet, basename="article")
router.register("comment", views.CommentViewSet, basename="comment")
app_name = "articles"

urlpatterns = [path("", include(router.urls))]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
