from .serializers import ArticleSerializer, CommentSerializer, ReCommentSerializer
from rest_framework import viewsets
from .models import Article, Comment, ReComment

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly

# Create your views here.


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Article.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            article=Article.objects.get(pk=self.kwargs.get("article_pk")),
        )

    def get_queryset(self):
        return super().get_queryset().filter(article=self.kwargs.get("article_pk"))


class ReCommentViewSet(viewsets.ModelViewSet):
    serializer_class = ReCommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = ReComment.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            article=Article.objects.get(pk=self.kwargs.get("article_pk")),
            parent=Comment.objects.get(pk=self.kwargs.get("comment_pk")),
        )

    def get_queryset(self):
        return super().get_queryset().filter(parent=self.kwargs.get("comment_pk"))
