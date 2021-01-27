from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from users.models import Subscription

User = get_user_model()


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'is_active', 'is_staff')
    list_editable = ('is_active', 'is_staff')
    list_filter = ('username', 'email', 'is_active', 'is_staff')
    search_fields = ('username', )


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
