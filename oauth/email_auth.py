from typing import Dict, Any

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class EmailTokenObtainSerializer(TokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:

        data = super().validate(attrs)

        if self.user.is_active is False:
            raise Exception("The user is inactive.")

        if self.user.email_verified is False:
            raise Exception("Please verify yourself via the email we sent you. "
                            "If you haven't received it, you can resend the verification email.." )

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['last_login'] = str(user.last_login)
        token['is_active'] = user.is_active
        token['email_verified'] = user.email_verified
        return token

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainSerializer
