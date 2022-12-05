from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
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


class PickViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


# 오늘의 메인 주제 랜덤픽
@api_view(["GET"])
def today_article(request):
    today_article = Article.objects.order_by("?").first()
    serializer = ArticleSerializer(today_article)
    Response(serializer.data)


# 밸런스게임 픽 카운트 통계
@api_view(["GET"])
def count_pick(request, game_pk):
    game = get_object_or_404(Article, pk=game_pk)
    all_pick = Pick.objects.all(article=game)
    A_pick = all_pick.filter(AB=1)
    B_pick = all_pick.filter(AB=2)
    A_percent = (A_pick.count() / all_pick.count()) * 100
    B_percent = (B_pick.count() / all_pick.count()) * 100

    pick_data = {
        "all_count": all_pick.count(),
        "A_count": A_pick.count(),
        "B_count": B_pick.count(),
        "A_percent": round(A_percent, 2),
        "B_percent": round(B_percent, 2),
    }
    Response(pick_data)


@api_view(["POST"])
def pick_AB(request, game_pk):
    if request.method == "POST":
        game = get_object_or_404(Article, pk=game_pk)
        pick = request.data["pick"]
        if pick == 1:
            game.A_count = game.A_count + 1
        else:
            game.B_count = game.B_count + 1
        game.save()
        if request.user.is_authenticated:
            Pick.objects.create(article=game, user=request.user, AB=pick)
        # 선택지 아티클에 저장 후 유저라면 선택기록 생성
        # 이후 되돌려보낼 픽카운트 통계 리스폰시키기
        all_pick = Pick.objects.all(article=game)
        A_pick = all_pick.filter(AB=1)
        B_pick = all_pick.filter(AB=2)
        A_percent = (A_pick.count() / all_pick.count()) * 100
        B_percent = (B_pick.count() / all_pick.count()) * 100

        pick_data = {
            "all_count": all_pick.count(),
            "A_count": A_pick.count(),
            "B_count": B_pick.count(),
            "A_percent": round(A_percent, 1),
            "B_percent": round(B_percent, 1),
        }
        Response(pick_data)
    else:
        Response({"message": "잘못된 접근입니다."})
