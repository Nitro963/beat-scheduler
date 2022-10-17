from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from . import models


class UserProfileAdmin(UserAdmin):
    list_per_page = 25
    exclude = ['last_login', 'version', 'is_superuser', 'groups', 'is_email_confirmed']
    readonly_fields = ['date_joined']
    list_display = ['id', 'name', 'gender', 'is_active']
    list_filter = ['is_active', 'is_staff', 'gender']
    search_fields = ['full_name']
    ordering = ['first_name', 'last_name', 'id']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'birthday', 'gender')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff'),
        }),
        (_('Important dates'), {'fields': ['date_joined']}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'birthday', 'gender')}),
    )

    def has_delete_permission(self, request, obj=None):
        if obj and obj.pk not in [1, 2]:
            return super(UserProfileAdmin, self).has_delete_permission(request, obj)
        return False

    def has_change_permission(self, request, obj=None):
        if obj and obj.pk == 1:
            return False
        return super(UserProfileAdmin, self).has_change_permission(request, obj)


class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class ContentAdmin(admin.ModelAdmin):
    list_per_page = 25
    search_fields = ['key', 'title']
    ordering = ['key', 'id']


admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.unregister(OutstandingToken)
admin.site.register(OutstandingToken, CustomOutstandingTokenAdmin)
