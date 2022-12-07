from django.shortcuts import render
from .models import Score

# Create your views here.

from rest_framework import response


def score(request):
    all_score = Score.objects.all()
    return response("테스트")
