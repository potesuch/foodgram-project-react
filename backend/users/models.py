from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Модель пользователя, основанная на стандартной модели AbstractUser.
    """
    pass


class Subscription(models.Model):
    """
    Модель подписки, представляющая связь между пользователями.

    Attributes:
        author (ForeignKey): Пользователь, на которого подписываются.
        user (ForeignKey): Пользователь, который подписывается.
    """
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
