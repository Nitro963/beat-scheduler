import datetime

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from patches.serializers import EnumField
from . import enums, mail
from . import models
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """serializes a user profile object"""
    gender = EnumField(enums.Gender)

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'first_name', 'last_name',
                  'birthday', 'gender', 'password', 'is_staff')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
            },
            'first_name': {
                'required': True,
            },
            'last_name': {
                'required': True,
            },
            'gender': {
                'required': True,
            },
            'is_staff': {
                'read_only': True,
            }
        }

    def validate_birthday(self, value): # noqa
        """
        Check that the birthday is not in the future.
        """
        if value > datetime.date.today():
            raise serializers.ValidationError(_("The date of birth is not valid"))
        return value

    def validate(self, data):
        # here data has all the fields which have validated values,
        # so we can create a User instance out of it
        user = UserProfile(**data)

        # get the password from the data
        password = data.get('password')

        errors = dict()
        try:
            # validate the password and catch the exception
            validate_password(password=password, user=user)

        # the exception raised here is different from serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(UserProfileSerializer, self).validate(data)

    def create(self, validated_data):
        """Create and return a new user"""
        user = models.UserProfile.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            birthday=validated_data['birthday'],
            gender=validated_data['gender'],
            password=validated_data['password'],
        )
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.refresh = attrs['refresh']
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
    )

    class Meta:
        fields = ['email']

    def validate_email(self, value): # noqa
        qs_email = models.UserProfile.objects.filter(email=value)
        if qs_email.exists():
            return value
        raise serializers.ValidationError(_("email does not exist"))

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = models.UserProfile.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None

        generator = mail.ResetPasswordTokenGenerator.instance
        if user is not None and generator.check_token(user, attrs['token']):
            attrs['user_pk'] = user.pk
            validate_password(password=attrs['password'], user=user)
            return attrs
        raise serializers.ValidationError(_("user not found"))

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class LogoutAllDevicesSerializer(serializers.Serializer):
    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class AuthUserSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
    )

    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    access = serializers.CharField(read_only=True)

    refresh = serializers.CharField(read_only=True)

    user = UserProfileSerializer(read_only=True)

    class Meta:
        fields = ('email', 'password')
