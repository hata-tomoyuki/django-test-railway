from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import User


class UserAdmin(BaseUserAdmin):
    # 管理画面で表示するフィールド
    list_display = ('account_id', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    # ユーザー編集画面のフィールドセット
    fieldsets = (
        (None, {'fields': ('account_id', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name', 'birth_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # ユーザー追加画面のフィールドセット
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account_id', 'email', 'password1', 'password2'),
        }),
    )

    search_fields = ('account_id', 'email', 'first_name', 'last_name')
    ordering = ('account_id',)


admin.site.register(User, UserAdmin)  # Userモデルを登録
admin.site.unregister(Group)  # Groupモデルは不要のため非表示にします
