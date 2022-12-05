from django.db import models
from django.conf import settings

# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=50)
    A = models.CharField(max_length=50)
    B = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    A_count = models.IntegerField(default=0)
    B_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=models.CASCADE
    )
    created_at = models.DateField(auto_now_add=True, null=False, blank=False)
    content = models.TextField()
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="comment_like")

    def __str__(self):
        return self.content


class Like(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="like_comment"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_like"
    )


class ReComment(models.Model):
    article = models.ForeignKey(
        Article,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="recomments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        Comment,
        related_name="soncomments",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    created_at = models.DateField(auto_now_add=True, null=False, blank=False)
    content = models.TextField()

    def __str__(self):
        return self.content


class Pick(models.Model):
    article = models.ForeignKey(
        Article, null=False, blank=False, on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=models.CASCADE
    )

    AB = models.IntegerField(default=0)
