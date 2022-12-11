from rest_framework import serializers
from articles.models import *
from profiles.models import Score, Profiles
from profiles.serializers import ProfileSerializer, BadgeSerializer


class ReCommentSerializer(serializers.ModelSerializer):
    userbadge = serializers.SerializerMethodField()

    def get_userbadge(self, obj):
        badge = Profiles.objects.get(user=obj.user).badge
        return BadgeSerializer(badge, read_only=True).data

    user = serializers.ReadOnlyField(source="user.nickname")
    parent = serializers.ReadOnlyField(source="parent.pk")
    article = serializers.ReadOnlyField(source="article.pk")

    class Meta:
        model = ReComment
        fields = [
            "pk",
            "article",
            "parent",
            "user",
            "userbadge",
            "content",
            "created_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    userbadge = serializers.SerializerMethodField()
    pick = serializers.SerializerMethodField()

    def get_userbadge(self, obj):
        badge = Profiles.objects.get(user=obj.user).badge
        return BadgeSerializer(badge, read_only=True).data

    def get_pick(self, obj):
        try:
            pick = Pick.objects.get(user=obj.user).AB
        except:
            pick = 0
        return pick

    user = serializers.ReadOnlyField(source="user.nickname")
    userpk = serializers.ReadOnlyField(source="user.pk")
    article = serializers.ReadOnlyField(source="article.pk")
    soncomments = ReCommentSerializer(many=True, read_only=True)
    # like_comment = serializers.StringRelatedField(many=True)
    total_likes = serializers.SerializerMethodField(read_only=True)
    like_users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "pk",
            "article",
            "user",
            "userpk",
            "userbadge",
            "content",
            "created_at",
            "soncomments",
            "total_likes",
            "like_users",
            "pick",
        ]

    def get_total_likes(self, comment):
        return comment.like_comment.count()

    def get_like_users(self, comment):
        likes = Like.objects.filter(comment=comment).values("user_id")
        users = []
        for like in likes:
            users.append(like["user_id"])

        return users


class ArticleSerializer(serializers.ModelSerializer):
    userbadge = serializers.SerializerMethodField()

    def get_userbadge(self, obj):
        badge = Profiles.objects.get(user=obj.user).badge
        return BadgeSerializer(badge, read_only=True).data

    user = serializers.ReadOnlyField(source="user.nickname")
    userpk = serializers.ReadOnlyField(source="user.pk")
    comments = CommentSerializer(many=True, read_only=True)
    best_A = serializers.SerializerMethodField()
    best_B = serializers.SerializerMethodField()

    def get_best_A(self, obj):
        comments = obj.comments.all()
        if not comments:
            return
        best_A = []
        for comment in comments:
            pick = 0
            try:
                pick = Pick.objects.get(article=obj, user=comment.user).AB
                if pick == 1:
                    total_likes = comment.like_comment.count()
                    best_A.append((total_likes, comment))
            except:
                return
        if not best_A:
            return
        best_A.sort(reverse=True)
        return CommentSerializer(best_A[0][1], read_only=True).data

    def get_best_B(self, obj):
        comments = obj.comments.all()
        best_B = []
        if not comments:
            return
        for comment in comments:
            pick = 0
            try:
                pick = Pick.objects.get(article=obj, user=comment.user).AB
                if pick == 2:
                    total_likes = comment.like_comment.count()
                    best_B.append((total_likes, comment))
            except:
                return
        if not best_B:
            return
        best_B.sort(reverse=True)
        return CommentSerializer(best_B[0][1], read_only=True).data

    class Meta:
        model = Article
        fields = [
            "pk",
            "title",
            "A",
            "B",
            "user",
            "userpk",
            "userbadge",
            "comments",
            "best_A",
            "best_B",
        ]


class LikeSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source="user.nickname")
    comment = serializers.ReadOnlyField(source="comment.pk")

    class Meta:
        model = Like
        fields = [
            "pk",
            "user",
            "comment",
        ]


# 유저가 아티클 (밸런스게임문제)중 A or B를 선택했을 때 ,
class PickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pick
        fields = "__all__"


class ListDataSerializer(serializers.ModelSerializer):
    ABcount = serializers.SerializerMethodField()
    userbadge = serializers.SerializerMethodField()

    def get_userbadge(self, obj):
        badge = Profiles.objects.get(user=obj.user).badge
        return BadgeSerializer(badge, read_only=True).data

    user = serializers.ReadOnlyField(source="user.nickname")

    def get_ABcount(self, obj):
        game = Article.objects.get(pk=obj.pk)
        if game.A_count > 0 or game.B_count > 0:
            all_pick = game.A_count + game.B_count
            A_percent = (game.A_count / all_pick) * 100
            B_percent = (game.B_count / all_pick) * 100
            ABcount = {
                "A_percent": round(A_percent, 1),
                "B_percent": round(B_percent, 1),
            }
        else:
            ABcount = {
                "A_percent": 0,
                "B_percent": 0,
            }
        return ABcount

    class Meta:
        model = Article
        fields = [
            "pk",
            "title",
            "A",
            "B",
            "user",
            "userbadge",
            "ABcount",
        ]


class GetArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")
    comment = serializers.SerializerMethodField()

    def get_comment(self, obj):
        comment = list(obj.comment_set.all())
        # comment = {"test": "테스트용"}
        return CommentSerializer(comment, many=True).data

    class Meta:
        model = Article
        fields = (
            "pk",
            "title",
            "A",
            "B",
            "user",
            "comment",
        )


class InfoArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("pk", "title", "A", "B")
