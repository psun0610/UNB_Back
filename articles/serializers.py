from rest_framework import serializers
from articles.models import Article, Comment, ReComment, Pick, Like


class ReCommentSerializer(serializers.ModelSerializer):

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
            "content",
            "created_at",
        ]


class CommentSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source="user.nickname")
    article = serializers.ReadOnlyField(source="article.pk")
    soncomments = ReCommentSerializer(many=True, read_only=True)
    # like_comment = serializers.StringRelatedField(many=True)
    total_likes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "pk",
            "article",
            "user",
            "content",
            "created_at",
            "soncomments",
            "total_likes",
        ]

    def get_total_likes(self, comment):
        return comment.like_comment.count()


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "pk",
            "title",
            "A",
            "B",
            "user",
            "comments",
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

    def get_ABcount(self, obj):
        game = Article.objects.get(pk=obj.pk)
        all_pick = game.A_count + game.B_count
        A_percent = (game.A_count / all_pick) * 100
        B_percent = (game.B_count / all_pick) * 100
        ABcount = {
            "A_percent": round(A_percent, 1),
            "B_percent": round(B_percent, 1),
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
