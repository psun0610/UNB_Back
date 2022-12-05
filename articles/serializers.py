from rest_framework import serializers
from articles.models import Article, Comment, Pick


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")

    class Meta:
        model = Article
        fields = (
            "pk",
            "title",
            "A",
            "B",
            "user",
        )


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")

    class Meta:
        model = Comment
        fields = [
            "id",
            "article",
            "user",
            "created_at",
            "comment",
        ]


# 유저가 아티클 (밸런스게임문제)중 A or B를 선택했을 때 ,
class PickSerializer(serializers.ModelSerializer):
    class Meta:
        models = Pick
        fields = "__all__"
