from allauth.account.adapter import get_adapter
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers, exceptions

from server.mors_seo import models


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('email',)


class CustomRegistrationSerializer(RegisterSerializer):
    fullname = serializers.CharField(required=True)

    def validate_fullname(self, fullname):
        fullname = get_adapter().clean_username(fullname)
        return fullname

    def get_cleaned_data(self):
        first_name, last_name = self.validated_data.get('fullname', ' ').split(' ')
        return {
            'first_name': first_name,
            'last_name': last_name,
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', '')
        }


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_username(self, username, password):
        if username and password:
            user = authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        if email and password:
            user = authenticate(email=email, password=password)
        elif username and password:
            user = authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            user = self._validate_username(username, password)
        else:
            user = self._validate_username_email(username, '', password)

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs
