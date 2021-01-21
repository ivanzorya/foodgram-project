from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["author"]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
