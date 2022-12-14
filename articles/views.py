from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import *
from profiles.models import Score
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly
from profiles.models import Grass
import datetime
import calendar
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from profiles.models import Score

today = datetime.date.today()


year = today.year
month = today.month
day = today.day
monthrange = calendar.monthrange(year, month)[1]

# 토픽 작성시에
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Article.objects.all()

    def perform_create(self, serializer):

        score = Score.objects.get(user=self.request.user)
        score.total += 20
        score.today += 20
        score.save()

        serializer.save(user=self.request.user)

    def retrieve(self, request, pk=None):
        queryset = Article.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = ArticleSerializer(user)
        try:
            score = Score.objects.get(user=request.user)
            if score.updated != today:
                score.today = 0
                score.save()
        except:
            pass
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        try:
            score = Score.objects.get(user=request.user)
            if score.updated != today:
                score.today = 0
                score.save()
        except:
            pass
        queryset = Article.objects.all().order_by("-pk")
        serializer = ListDataSerializer(queryset, many=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ListDataSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


# @api_view(["GET"])
# def get_article(request, article_pk):
#     article = get_object_or_404(Article, pk=article_pk)
#     try:
#         score = Score.objects.get(user=request.user)
#         if score.updated != today:
#             score.today = 0
#             score.save()
#     except:
#         pass
#     if request.method == "GET":
#         serializers = GetArticleSerializer(article)
#         print(serializers.data)
#         return Response(serializers.data)


#  댓글 작성시에
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Comment.objects.all()

    def perform_create(self, serializer):

        score = Score.objects.get(user=self.request.user)

        score.total += 5
        score.today += 5
        score.save()

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
# @api_view(["GET"])
# def today_article(request):
#     today_article = Article.objects.order_by("?").first()
#     serializer = ArticleSerializer(today_article)
#     return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def random_article(request):
    random_article = Article.objects.order_by("?").first()
    article = random_article.pk
    print(random_article)
    now = datetime.datetime.now()
    return Response({"article_pk": article, "now": now})


#  픽 추가시에


@api_view(["POST", "GET"])
@permission_classes([AllowAny])
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
                Pick.objects.create(user=request.user, AB=pick, article=game)

                score = Score.objects.get(user=request.user)
                score.total += 10
                score.today += 10
                score.save()

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
        # A_percent = (A_pick / all_pick) * 100
        # B_percent = (B_pick / all_pick) * 100

        data = {
            "all_count": all_pick,
            "A_count": A_pick,
            "B_count": B_pick,
            # "A_percent": round(A_percent, 1),
            # "B_percent": round(B_percent, 1),
        }
        return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def today_article(request):

    allScore = Score.objects.all()
    for score in allScore:
        if score.updated != today:
            score.today = 0
            score.save()
    all_today_articles = TodayTopic.objects.all()
    today_articles = TodayTopic.objects.filter(created_at=today)
    if len(today_articles) == 0:
        print("오늘의 아티클 생성")
        random_article = Article.objects.order_by("?").first()
        print(random_article, "1")
        TodayTopic.objects.create(article=random_article)
        print("투데이 아티클 만듬")
        today_articles = TodayTopic.objects.filter(created_at=today)
        today_article_pk = today_articles[0].article.pk
        return Response({"article_pk": today_article_pk})
    else:
        print("오늘의 아티클 가져오기")
        today_articles = TodayTopic.objects.filter(created_at=today)
        today_article_pk = today_articles[0].article.pk
        return Response({"article_pk": today_article_pk})
