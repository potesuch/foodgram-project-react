from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer

from recipes.models import (Tag, Ingredient, Recipe, Favorite, ShoppingCart,
                            AmountIngredient)
from users.models import Subscription
from .fields import Base64ImageField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для создания пользователя.
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        extra_kwargs = {field: {'required': True} for field in fields}


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для пользователя, включающий информацию о подписке.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на данного автора.

        Args:
            obj: Объект пользователя.

        Returns:
            bool: True, если подписан, иначе False.
        """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Краткий сериализатор для рецепта.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    """
    Сериализатор для подписки, включающий рецепты автора и их количество.
    """
    recipes = ShortRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов у автора.

        Args:
            obj: Объект пользователя.

        Returns:
            int: Количество рецептов.
        """
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        """
        Всегда возвращает True для подтверждения подписки.

        Args:
            obj: Объект пользователя.

        Returns:
            bool: Всегда True.
        """
        return True


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тега.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиента.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецепта, включающий информацию о тегах, авторе, ингредиентах, 
    и проверку на нахождение в избранном или в корзине покупок.
    """
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        """
        Проверяет, находится ли рецепт в избранном у текущего пользователя.

        Args:
            obj: Объект рецепта.

        Returns:
            bool: True, если в избранном, иначе False.
        """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, находится ли рецепт в корзине покупок у текущего пользователя.

        Args:
            obj: Объект рецепта.

        Returns:
            bool: True, если в корзине покупок, иначе False.
        """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def create(self, validated_data):
        """
        Создает новый рецепт с тегами и ингредиентами.

        Args:
            validated_data: Данные для создания рецепта.

        Returns:
            Recipe: Созданный объект рецепта.
        """
        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            current_ingredient = Ingredient.objects.get(**ingredient)
            AmountIngredient.objects.create(ingredient=current_ingredient,
                                            recipe=recipe, amount=amount)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт с новыми тегами и ингредиентами.

        Args:
            instance: Объект рецепта для обновления.
            validated_data: Данные для обновления рецепта.

        Returns:
            Recipe: Обновленный объект рецепта.
        """
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            current_ingredient = Ingredient.objects.get(**ingredient)
            AmountIngredient.objects.create(ingredient=current_ingredient,
                                            recipe=recipe, amount=amount)
        return recipe
