from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Subscription(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='in_subscriptions')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='subscriptions')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
