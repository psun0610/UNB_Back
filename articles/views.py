from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
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

    def retrieve(self, request, pk=None):
        queryset = Article.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = ArticleSerializer(user)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = Article.objects.all()
        serializers = ListDataSerializer(queryset, many=True)
        return Response(serializers.data)


@api_view(["GET"])
def get_article(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    # print(article)
    if request.method == "GET":
        serializers = GetArticleSerializer(article)
        print(serializers.data)
        return Response(serializers.data)


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


class LikeCreate(generics.ListCreateAPIView, mixins.DestroyModelMixin):
    serializer_class = LikeSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        comment = Comment.objects.get(pk=self.kwargs.get("comment_pk"))
        return Like.objects.filter(user=user, comment=comment)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.save(
            user=self.request.user,
            comment=Comment.objects.get(pk=self.kwargs.get("comment_pk")),
        )


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
    return Response(serializer.data)


# 밸런스게임 픽 카운트 통계
# @api_view(["GET"])
# def count_pick(request, game_pk):
#     game = get_object_or_404(Article, pk=game_pk)
#     all_pick = Pick.objects.all(article=game)
#     A_pick = all_pick.filter(AB=1)
#     B_pick = all_pick.filter(AB=2)
#     A_percent = (A_pick.count() / all_pick.count()) * 100
#     B_percent = (B_pick.count() / all_pick.count()) * 100

#     pick_data = {
#         "all_count": all_pick.count(),
#         "A_count": A_pick.count(),
#         "B_count": B_pick.count(),
#         "A_percent": round(A_percent, 2),
#         "B_percent": round(B_percent, 2),
#     }
#     return Response(pick_data)


@api_view(["POST", "GET"])
def pick_AB(request, game_pk):
    game = get_object_or_404(Article, pk=game_pk)
    if request.method == "POST":
        pick = request.data["pick"]
        print(pick)
        if pick == 1:
            game.A_count = game.A_count + 1
        else:
            game.B_count = game.B_count + 1
        game.save()
        if request.user.is_authenticated:
            picked = Pick.objects.filter(Q(article=game) & Q(user=request.user))
            if picked:
                picked[0].AB = pick
                picked[0].save()
                print("변경")
            else:
                Pick.objects.create(article=game, user=request.user, AB=pick)
                print("생성")
        # 선택지 아티클에 저장 후 유저라면 선택기록 생성
        # 이후 되돌려보낼 픽카운트 통계 리스폰시키기
        all_pick = game.A_count + game.B_count
        A_pick = game.A_count
        B_pick = game.B_count
        A_percent = (A_pick / all_pick) * 100
        B_percent = (B_pick / all_pick) * 100

        data = {
            "all_count": all_pick,
            "A_count": A_pick,
            "B_count": B_pick,
            "A_percent": round(A_percent, 1),
            "B_percent": round(B_percent, 1),
        }

        return Response(data)
    else:
        all_pick = game.A_count + game.B_count
        A_pick = game.A_count
        B_pick = game.B_count
        A_percent = (A_pick / all_pick) * 100
        B_percent = (B_pick / all_pick) * 100

        data = {
            "all_count": all_pick,
            "A_count": A_pick,
            "B_count": B_pick,
            "A_percent": round(A_percent, 1),
            "B_percent": round(B_percent, 1),
        }
        return Response(data)


@api_view(["POST"])
def like_comment(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    if comment.like.filter(user=request.user).exists():
        comment.like.remove(request.user)
    else:
        comment.like.add(request.user)

    data = {
        "like_counts": len(comment.like.all()),
        "is_likeed": comment.like.filter(user=request.user).exists(),
    }
    return Response(data)
