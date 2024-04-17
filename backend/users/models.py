from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Subscription(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='in_subscriptions',
                               verbose_name='Автор')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='subscriptions',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (models.constraints.UniqueConstraint(
            fields=('author', 'user'),
            name='unique_subscription'
        ),)
