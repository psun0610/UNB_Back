from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from rest_framework.response import Response
import datetime
from rest_framework.permissions import AllowAny

# Create your views here.


today = datetime.date.today()


def score(request):
    all_score = Score.objects.all()
    return Response("테스트")


@api_view(["GET"])
@permission_classes([AllowAny])
def best_user(request):
    scores = Score.objects.filter(updated=today).order_by("-today")[:3]
    if len(scores) == 0:
        return Response("베스트유저 없음")
    else:
        serializers = ScoreSerializer(scores, many=True)
        return Response(serializers.data)
