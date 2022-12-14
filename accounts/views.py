import requests
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from rest_framework import status, permissions
from rest_framework.response import Response
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount
from .models import User
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from profiles.serializers import *
from profiles.models import *
from django.db.models import Q
from accounts.permissions import IsOwnerOrReadOnly
import datetime
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

state = getattr(settings, "STATE")
BASE_URL = "https://www.unbback.cf/"
GOOGLE_CALLBACK_URI = "https://www.unbalace.cf/login"

today = datetime.date.today()


def google_login(request):
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}"
    )


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def google_callback(request):
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get("code")
    print(code)
    """
    Access Token Request
    """
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
    )
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    )
    email_req_status = email_req.status_code
    if email_req_status != 200:
        return JsonResponse(
            {"err_msg": "failed to get email"}, status=status.HTTP_400_BAD_REQUEST
        )
    email_req_json = email_req.json()
    email = email_req_json.get("email")
    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse(
                {"err_msg": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "google":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 기존에 Google로 가입된 유저
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


KAKAO_CALLBACK_URI = "https://www.unbalace.cf/login"  # 프론트 로그인 URI 입력


def kakao_login(request):
    rest_api_key = getattr(settings, "SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email"
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def kakao_callback(request):
    rest_api_key = getattr(settings, "SOCIAL_AUTH_KAKAO_CLIENT_ID")  # 카카오 앱키, 추후 시크릿 처리
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}"
    )
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    kakao_account = profile_json.get("kakao_account")
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    email = kakao_account.get("email")
    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse(
                {"err_msg": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "kakao":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 기존에 kakao로 가입된 유저
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)
        # user의 pk, email, first name, last name과 Access Token, Refresh token 가져옴
        accept_json = accept.json()
        accept_json.pop("user", None)
        return Response(accept_json)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "https://www.unbalace.cf/login"


# 유저 페이지 확인 (유저정보 및 유저 작성한 글 확인 )
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsOwnerOrReadOnly])
def my_page(request, user_pk):
    if request.method == "GET":

        user_info = get_object_or_404(User, pk=user_pk)
        comment = Comment.objects.filter(user=user_info)
        serializers = UserInfo(user_info)
        # user_article = Article.objects.filter(user=request.user)
        user_comment = Comment.objects.filter(user=user_info)
        user_recomment = ReComment.objects.filter(user=user_info)
        # user_profile = Profiles.objects.get(user=user_info)
        user_score = Score.objects.get(user=user_info)
        user_grass = Grass.objects.get(user=user_info)
        # user_pick = Pick.objects.filter(user=request.user)
        user_like_comment = Like.objects.filter(user=user_info)
        comment = []
        likecomment = []
        for c in user_like_comment:
            likecomment.append(c.comment.pk)
        for c in user_comment:

            comment.append(
                {
                    "content": c.content,
                    "article_pk": c.article.pk,
                    "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
                    "article": c.article.title,
                    "A": c.article.A,
                    "B": c.article.B,
                }
            )
        for r in user_recomment:
            comment.append(
                {
                    "content": r.content,
                    "article_pk": r.article.pk,
                    "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
                    "parent": r.parent.pk,
                    "article": r.parent.article.title,
                    "A": r.parent.article.A,
                    "B": r.parent.article.B,
                }
            )
        all_data = {
            "user_pk": user_pk,
            "comment": comment,
            "likecomment": likecomment,
            "userinfo": serializers.data,
            # "grade": user_profile.grade,
            "all_score": user_score.total,
            "today_score": user_score.today,
            #  user_grass
            "year": user_grass.year,
            "month": user_grass.month,
            "monthrange": user_grass.monthrange,
            "daylist": user_grass.daylist,
            "consecutive": user_grass.consecutive,
        }
        return Response(all_data)

    # 유저정보 수정 put메서드 사용 (raise_exception=True<- (commit=True)와 같은 역활
    elif request.method == "PUT":
        if request.user.is_authenticated:
            user_pk = request.data["user_pk"]
            badge_pk = request.data["badge_pk"]
            user = User.objects.get(pk=user_pk)
            badge = get_object_or_404(Badge, pk=badge_pk)
            profile = Profiles.objects.get(user=user)
            profile.badge = badge
            profile.save()
            badgeSerializer = BadgeDetailSerializer(badge)
            return Response(badgeSerializer.data, status=200)
    elif request.method == "PATCH":
        if request.user.is_authenticated:
            nickname = request.data["nickname"]
            user = User.objects.get(pk=user_pk)
            user.nickname = nickname
            user.save()
            userSerializer = CustomUserDetailsSerializer(user)
            return Response(userSerializer.data, status=200)
    elif request.method == "DELETE":
        if request.user.is_authenticated:
            user = User.objects.get(pk=user_pk)
            if user != request.user:
                return Response({"result": "본인만 삭제 할 수 있습니다."})
            user.delete()
            return Response({"result": "user delete"})


# class DeleteAccount(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def delete(self, request, *args, **kwargs):
#         user = self.request.user
#         user.delete()

#         return Response({"result": "user delete"})
