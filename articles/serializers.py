from rest_framework import serializers
from articles.models import Article, Comment, ReComment, Pick, Like, Score


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
