import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt import serializers as jwt_serializers
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from . import mail
from . import signals
from . import models
from . import filters
from . import serializers


class UserRegisterViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """Handle creating users"""

    serializer_class = serializers.UserProfileSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.create(request.data)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = mail.EmailConfirmationTokenGenerator.instance.make_token(user)
            link = reverse('users-confirm-email', args=[token, uid], request=request)

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            html_message = render_to_string('mail/activate_account.html', context={'instance': user,
                                                                                   'time': timezone.now(),
                                                                                   'link': link,
                                                                                   'ip': ip})
            plain_message = strip_tags(html_message)
            # TODO send mails
            # send_mail.delay(subject='Account activation', message=plain_message,
            #                 html_message=html_message,
            #                 recipient_list=[user.email],
            #                 from_email=None)

            data = {'details': 'In order to complete registration process, '
                               'we have sent an email with a confirmation link to your email address.'}

            return Response(data,
                            status=status.HTTP_201_CREATED)


class UserLoginViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """Handle getting authentication token and users login"""
    serializer_class = serializers.AuthUserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request=request,
                            username=email, password=password)

        if not user:
            return Response(
                {
                    'details': _('Unable to log in with provided credentials.')
                },
                status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_email_confirmed:
            return Response(
                {
                    'details': _('Your email should be confirmed')
                },
                status=status.HTTP_403_FORBIDDEN)

        if user.is_active:
            token = RefreshToken.for_user(user)
            token['version'] = str(user.version)
            update_last_login(None, user)

            obj = {
                'refresh': str(token),
                'access': str(token.access_token),
                'user': user,
                'wallets': user.wallets,
            }
            return Response(serializer.to_representation(obj), status=status.HTTP_200_OK)

        return Response(
            {
                'details': _('Your account has been disabled.')
            },
            status=status.HTTP_403_FORBIDDEN)


class UsersViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin, mixins.ListModelMixin):
    """Handle users retrieval and updates"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    ordering_fields = ('full_name', 'birthday',)
    search_fields = ('full_name', 'email',)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = filters.UserProfileFilter

    @action(url_name='confirm-email',
            url_path='confirm-email/(?P<token>[0-9A-Za-z]+-[0-9A-Za-z]+)/(?P<uidb64>([a-z0-9_A-Z]|-)+)',
            permission_classes=(AllowAny,),
            authentication_classes=[],
            detail=False, methods=['get'])
    def confirm_email(self, request, token, uidb64, *args, **kwargs): # noqa
        not_found = HttpResponse(status=status.HTTP_404_NOT_FOUND)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = models.UserProfile.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None
        generator = mail.EmailConfirmationTokenGenerator.instance
        if user is not None and generator.check_token(user, token):
            user.is_email_confirmed = True
            user.save()
            signals.email_confirmed.send(sender=self, instance=user)
        else:
            return not_found

        return redirect(settings.FRONTEND_DOMAIN + '/login/')


class UserLogoutViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.LogoutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = serializer.validated_data['refresh']
            RefreshToken(refresh).blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.ResetPasswordSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_pk = serializer.validated_data['user_pk']
        password = serializer.validated_data['password']
        user = models.UserProfile.objects.get(pk=user_pk)
        user.set_password(password)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ForgotPasswordViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.ForgotPasswordSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = models.UserProfile.objects.get(email=serializer.validated_data['email'])
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = mail.ResetPasswordTokenGenerator.instance.make_token(user)
            link = reverse('password-reset-password', args=[token, uid], request=request)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            html_message = render_to_string('mail/reset_password.html', context={'link': link,
                                                                                 'ip': ip,
                                                                                 'instance': user,
                                                                                 'time': timezone.now()})
            plain_message = strip_tags(html_message)
            # TODO send mail
            # send_mail.delay(subject='Reset Password',
            #                 message=plain_message,
            #                 html_message=html_message,
            #                 recipient_list=[user.email],
            #                 from_email=None)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(url_name='reset-password',
            url_path='reset-password/(?P<token>[0-9A-Za-z]+-[0-9A-Za-z]+)/(?P<uidb64>([a-z0-9_A-Z]|-)+)',
            permission_classes=(AllowAny,),
            authentication_classes=[],
            detail=False, methods=['get'])
    def reset_password(self, request, token, uidb64, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = models.UserProfile.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None

        generator = mail.ResetPasswordTokenGenerator.instance
        if user is not None and generator.check_token(user, token):
            # TODO update url redirection
            return redirect('http://localhost:3000' + '/reset-password?' + 'token=' + token + '&' + 'uidb64=' + uidb64)
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


class UserLogoutAllDevicesViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.LogoutAllDevicesSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.version = uuid.uuid4()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenViewSet(viewsets.ViewSetMixin, jwt_views.TokenViewBase):
    """
    Handles JWT Token manipulation.
    """

    @action(methods=['post'], detail=False, serializer_class=jwt_serializers.TokenRefreshSerializer)
    def refresh(self, request, *args, **kwargs):
        return super(TokenViewSet, self).post(request, *args, **kwargs)

    @action(methods=['post'], detail=False, serializer_class=jwt_serializers.TokenVerifySerializer)
    def verify(self, request, *args, **kwargs):
        """
        Takes a token and indicates if it is valid.
        This view provides no information about a token's fitness for a particular use.
        """
        return super(TokenViewSet, self).post(request, *args, **kwargs)
