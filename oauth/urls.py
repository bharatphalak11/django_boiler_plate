from django.urls import  path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from oauth.email_auth import EmailTokenObtainPairView
from oauth.google_auth import GoogleAuthView

urlpatterns = [
    path('', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify', TokenVerifyView.as_view(), name='token_verify'),
    path('google', GoogleAuthView.as_view(), name='google'),
]