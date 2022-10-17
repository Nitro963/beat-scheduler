import datetime
import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Value, CharField
from django.db.models.functions import Concat

from .enums import Gender


class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, email, first_name, last_name, birthday, gender, password,
                    is_email_confirmed=False,
                    is_active=True,
                    is_staff=False):
        """Create a new user profile"""
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name,
                          birthday=birthday, gender=gender, is_staff=is_staff,
                          is_active=is_active, is_email_confirmed=is_email_confirmed)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, gender, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, first_name=first_name, last_name=last_name, password=password,
                                birthday=datetime.date.today(), gender=gender)
        user.is_superuser = True
        user.is_staff = True
        user.is_email_confirmed = True
        user.save(using=self._db)
        return user

    def get_queryset(self):
        return super(UserProfileManager, self).get_queryset().annotate(full_name=Concat('first_name', Value(' '),
                                                                                        'last_name',
                                                                                        output_field=CharField()))


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""

    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)

    password = models.CharField(max_length=128,
                                validators=[MinLengthValidator(8, message='Password must be at least 8 characters')])

    first_name = models.CharField(max_length=25, default='')

    last_name = models.CharField(max_length=25, default='')

    birthday = models.DateField()

    gender = models.CharField(max_length=1, choices=Gender.get_django_choices(), default=Gender.Male.value)

    is_active = models.BooleanField(default=True,
                                    help_text='Designates that this user account is activated')

    is_email_confirmed = models.BooleanField(default=False,
                                             help_text='Designates that user email is confirmed')

    is_staff = models.BooleanField(default=False,
                                   help_text='Designates that this user has access to the admin panel.')

    date_joined = models.DateField(default=datetime.date.today, editable=False)

    version = models.UUIDField(default=uuid.uuid4)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['birthday']),
            models.Index(fields=['gender']),
            models.Index(fields=['first_name', 'last_name'])
        ]

    def __str__(self):
        """Return string representation of user"""
        return self.email

    def name(self):
        """Retrieve full name for user"""
        return f'{self.first_name} {self.last_name}'
