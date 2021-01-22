from django.contrib import admin

from users.models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")


admin.site.register(Subscription, SubscriptionAdmin)