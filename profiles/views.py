from django.shortcuts import render
from .models import Score

# Create your views here.
from .serializers import ScoreSerializer
from rest_framework import response


def score(request):
    all_score = Score.objects.all()
    serializer = ScoreSerializer(all_score, many=True)
    response(serializer.data)
