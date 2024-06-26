from django.db import models

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    """
    Модель тега для рецептов.

    Attributes:
        name (CharField): Название тега.
        color (CharField): Цвет тега.
        slug (SlugField): Уникальный идентификатор тега.
    """
    name = models.CharField('Тэг', max_length=100, unique=True)
    color = models.CharField('Цвет', max_length=7, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингредиента для рецептов.

    Attributes:
        name (CharField): Название ингредиента.
        measurement_unit (CharField): Единица измерения ингредиента.
    """
    name = models.CharField('Название', max_length=100)
    measurement_unit = models.CharField('Еденица измерения', max_length=20)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (models.UniqueConstraint(
            fields=('name', 'measurement_unit'), name='unique_ingredient'
        ),)


class Recipe(models.Model):
    """
    Модель рецепта.

    Attributes:
        tags (ManyToManyField): Теги, связанные с рецептом.
        author (ForeignKey): Автор рецепта.
        ingredients (ManyToManyField): Ингредиенты, связанные с рецептом.
        name (CharField): Название рецепта.
        image (ImageField): Изображение рецепта.
        text (TextField): Описание рецепта.
        cooking_time (PositiveSmallIntegerField): Время приготовления в минутах.
    """
    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  verbose_name='Тэги')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes', verbose_name='Автор')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AmountIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField('Имя', max_length=200)
    image = models.ImageField('Изображение', upload_to='recipes/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(
            1, message='Минимальное время приготовления 1 минута'),
        )
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class AmountIngredient(models.Model):
    """
    Модель количества ингредиентов в рецепте.

    Attributes:
        ingredient (ForeignKey): Связанный ингредиент.
        recipe (ForeignKey): Связанный рецепт.
        amount (PositiveSmallIntegerField): Количество ингредиента.
    """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='amount_recipes',
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='amount_ingredients',
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(MinValueValidator(
            1, message='Минимальное количествво ингредиентов 1'),
        )
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количества ингредиентов'


class ShoppingCart(models.Model):
    """
    Модель корзины покупок.

    Attributes:
        recipe (ForeignKey): Рецепт в корзине.
        user (ForeignKey): Пользователь, владеющий корзиной.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_shopping_carts',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_carts',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = (models.constraints.UniqueConstraint(
            fields=('recipe', 'user'),
            name='unique_shopping_cart'
        ),)


class Favorite(models.Model):
    """
    Модель избранного рецепта.

    Attributes:
        recipe (ForeignKey): Избранный рецепт.
        user (ForeignKey): Пользователь, добавивший рецепт в избранное.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_favorites',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (models.constraints.UniqueConstraint(
            fields=('recipe', 'user'),
            name='unique_favorite'
        ),)
