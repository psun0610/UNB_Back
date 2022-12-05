from rest_framework import serializers
from articles.models import Article, Comment, ReComment


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

    class Meta:
        model = Comment
        fields = [
            "pk",
            "article",
            "user",
            "content",
            "created_at",
            "soncomments",
        ]


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
