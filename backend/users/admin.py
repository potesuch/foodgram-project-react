from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомизация отображения модели User в административной панели.
    """
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Кастомизация отображения модели Subscription в административной панели.
    """
    list_display = ('author', 'user')
