from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'nickname', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
        ('Profile', {'fields': ('bio', 'phone', 'profile_images', 'nickname')}),
    )