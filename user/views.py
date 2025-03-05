import hashlib
import os
from datetime import timedelta

from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from user.mail import send_verify_email, send_forgot_password_email
from django.http import HttpResponseRedirect
from django.conf import settings
import django_filters

class UserCreditTransactionsFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    date_joined = django_filters.DateFilter(field_name='date_joined', lookup_expr='date')

    class Meta:
        model = User
        exclude = ['avatar']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'email_code', 'email_code_created_date', 'forgot_password_code',
                   'forgot_password_code_created_date', 'social_auth']

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'is_admin', 'is_active', 'email_verified', 'email_code',
                   'email_code_created_date', 'forgot_password_code', 'forgot_password_code_created_date',
                   'email', 'social_auth']
    
    def to_representation(self, instance):
        return UserSerializer(instance=instance).data


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['email_code']
        extra_kwargs = {'is_admin': {'read_only': True}, 'is_active': {'read_only': True}, 'last_login': {'read_only': True}, 'email_verified': {'read_only': True}, 'password': {'write_only': True},}

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        UserViewSet.set_unique_avatar_name(validated_data)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserViewSet.send_verify_email(user)
        return user

    def to_representation(self, instance):
        return UserSerializer(instance=instance).data


class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']


class IsAdminOrIsSelf(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_admin


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filterset_class = UserCreditTransactionsFilter
    ordering_fields = '__all__'
    ordering = ['-id']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_permissions(self):
        common_permissions: list = [IsAuthenticated]

        match self.action:
            case 'list' | 'destroy':
                permission_classes = [*common_permissions, IsAdminUser]
            case 'retrieve' | 'update' | 'change_password':
                permission_classes = [*common_permissions, IsAdminOrIsSelf]
            case 'create' |'forgot_password' | 'reset_password' | 'resend_verify_email' | 'verify_email':
                permission_classes = []
            case _:
                permission_classes = common_permissions

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
            match self.action:
                case 'create':
                    return CreateUserSerializer
                case 'update':
                    return UpdateUserSerializer
                case 'reset_password':
                    return ResetPasswordSerializer
                case 'verify_email':
                    return None
                case 'send_verify_email':
                    return None
                case _:
                    return UserSerializer

    @staticmethod
    def set_unique_avatar_name(data):
        if data.get('avatar'):
            avatar_name: str = data['avatar'].name

            avatar_name_exists: bool = User.objects.filter(avatar=f'avatar/{avatar_name}').exists()

            if avatar_name_exists:
                unique_string = get_random_string(6)
                avatar_name = f'{unique_string}_' + avatar_name

            data['avatar'].name = avatar_name

        return None

    @action(methods=['post'], detail=False, url_path='forgot-password')
    @transaction.atomic
    def forgot_password(self, request, *args, **kwargs):
        email: str = request.data['email']

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise ValidationError(detail="User not Found!",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        UserViewSet.send_forgot_password_email(user)

        return Response({'status': True})

    @action(methods=['post'], detail=True, url_path='reset-password')
    @transaction.atomic
    def reset_password(self, request, pk):
        user: User = self.get_object()
        password = request.data['password']
        code: str = request.data['forgot_password_code']

        if user.forgot_password_code is None:
            raise ValidationError(detail="The forgot password code was not generated.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        if timezone.now() > user.forgot_password_code_created_date + timedelta(minutes=100):
            raise ValidationError(detail="The verification code has expired. Please resend the code.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        if user.forgot_password_code != code:
            raise ValidationError(detail="Invalid forgot password code.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        if user.check_password(password) is True:
            raise ValidationError(detail="You have already used this password before. Please try a new one.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        user.set_password(password)
        user.forgot_password_code = None
        user.forgot_password_code_created_date = None
        user.save()
        return Response({'status': True})


    @staticmethod
    def send_forgot_password_email(user: User):
        user.forgot_password_code = hashlib.sha256(os.urandom(16)).hexdigest()
        user.forgot_password_code_created_date = timezone.now()
        user.save()
        link = f"Don't know for know, forgot pasqord code:- {user.forgot_password_code}"
        send_forgot_password_email(user, link)
        return None


    @staticmethod
    def send_verify_email(user: User):
        user.email_code = hashlib.sha256(os.urandom(16)).hexdigest()
        user.email_code_created_date = timezone.now()
        user.save()
        link = settings.SERVER_HOST + '/api/user/' + f'{user.id}/verify-email/?email_code={user.email_code}'
        send_verify_email(user, link)
        return None

    @action(methods=['get'], detail=False, url_path='resend-verify-email')
    @transaction.atomic
    def resend_verify_email(self, request, *args, **kwargs):
        email: str = request.query_params['email']

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise ValidationError(detail="User not Found!",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        if user.email_verified is True:
            raise ValidationError(detail="User already verified!", code=status.HTTP_412_PRECONDITION_FAILED)

        UserViewSet.send_verify_email(user)
        return Response({'status': True})

    @action(methods=['GET'], detail=True, url_path='verify-email')
    @transaction.atomic
    def verify_email(self, request, pk):
        user: User = self.get_object()
        code: str = request.query_params['email_code']

        if user.email_verified is True:
            raise ValidationError(detail="User already verified!", code=status.HTTP_412_PRECONDITION_FAILED)

        if user.email_code_created_date is None:
            raise ValidationError(detail="The verification code was not generated.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        if timezone.now() > user.email_code_created_date + timedelta(minutes=10):
            raise ValidationError(detail="The verification code has expired. Please resend the code.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        if user.email_code != code:
            raise ValidationError(detail="Invalid verification code.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        user.email_verified = True
        user.email_code = None
        user.email_code_created_date = None
        user.save()

        return HttpResponseRedirect(redirect_to=settings.WEB_HOST)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        UserViewSet.set_unique_avatar_name(request.data)
        return super().update(request, *args, **kwargs)

    @action(methods=['PATCH'], detail=True, url_path='change-password')
    @transaction.atomic
    def change_password(self, request, pk):
        user: User = self.get_object()
        request_data: dict = request.data
        old_password: str = request_data['old_password']
        new_password: str = request_data['new_password']
        confirm_password: str = request_data['confirm_password']

        # Check if the old password is correct.
        if not user.check_password(old_password):
            raise ValidationError(detail="Old password is not correct.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        # Check if new password and confirm password match.
        if new_password != confirm_password:
            raise ValidationError(detail="New and confirmation password do not match.",
                                  code=status.HTTP_412_PRECONDITION_FAILED)

        # Set the new password.
        user.set_password(new_password)
        user.save()

        return Response(data={'message': 'Password changed successfully!'}, status=status.HTTP_200_OK)

    # Made this url for code testing purpose.
    @action(methods=['POST'], detail=False, url_path='test')
    @transaction.atomic
    def test(self, request, *args, **kwargs):

        return Response(data={'message': 'Successfully!'}, status=status.HTTP_200_OK)
