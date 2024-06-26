from collections import defaultdict
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet

from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import Subscription
from .serializers import (SubscriptionSerializer, TagSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer)
from .permissions import IsAuthorOrStuffOrReadOnly, IsAdminOrReadOnly
from .pagination import LimitedPageNumberPagination
from .filters import IngredientFilter, RecipeFilter

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    Кастомное представление для пользователей, включая подписки и управление ими.
    """
    pagination_class = LimitedPageNumberPagination

    @action(['get'], detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """
        Получает список подписок текущего пользователя.

        Args:
            request: Текущий запрос.

        Returns:
            Response: Ответ с сериализованными данными подписок.
        """
        queryset = User.objects.filter(in_subscriptions__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(['post'], detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        """
        Подписывается на указанного пользователя.

        Args:
            request: Текущий запрос.
            args: Дополнительные аргументы.
            kwargs: Дополнительные аргументы.

        Returns:
            Response: Ответ с сериализованными данными подписки.

        Raises:
            exceptions.NotFound: Если пользователь не найден.
        """
        try:
            author = User.objects.get(pk=kwargs.get('id'))
        except User.DoesNotExist:
            raise exceptions.NotFound
        Subscription.objects.get_or_create(user=request.user, author=author)
        serializer = SubscriptionSerializer(author)
        return Response(serializer.data)

    @subscribe.mapping.delete
    def unsubscribe(self, request, *args, **kwargs):
        """
        Отписывается от указанного пользователя.

        Args:
            request: Текущий запрос.
            args: Дополнительные аргументы.
            kwargs: Дополнительные аргументы.

        Returns:
            Response: Ответ с сериализованными данными отписки.

        Raises:
            exceptions.NotFound: Если пользователь или подписка не найдены.
            exceptions.ParseError: Если пользователь не подписан.
        """
        try:
            author = User.objects.get(pk=kwargs.get('id'))
        except User.DoesNotExist:
            raise exceptions.NotFound
        try:
            subscription = Subscription.objects.get(user=request.user,
                                                    author=author)
        except Subscription.DoesNotExist:
            raise exceptions.ParseError(
                'Вы не подписаны на этого пользователя'
            )
        subscription.delete()
        serializer = SubscriptionSerializer(author)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для тегов, доступное только для чтения.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для ингредиентов, доступное только для чтения.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Представление для рецептов с возможностью управления, фильтрации и пагинации.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrStuffOrReadOnly,)
    pagination_class = LimitedPageNumberPagination
    filterset_class = RecipeFilter

    def partial_update(self, request, *args, **kwargs):
        """
        Запрещает частичное обновление (PATCH) для рецептов.

        Args:
            request: Текущий запрос.
            args: Дополнительные аргументы.
            kwargs: Дополнительные аргументы.

        Raises:
            exceptions.MethodNotAllowed: Если метод PATCH используется.
        """
        raise exceptions.MethodNotAllowed('PATCH')

    def perform_update(self, serializer):
        """
        Сохраняет обновленный рецепт с указанием автора.

        Args:
            serializer: Сериализатор рецепта.
        """
        serializer.save(author=self.request.user)

    def perform_create(self, serializer):
        """
        Создает новый рецепт с указанием автора.

        Args:
            serializer: Сериализатор рецепта.
        """
        serializer.save(author=self.request.user)

    @action(['post'], detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        """
        Добавляет рецепт в избранное.

        Args:
            request: Текущий запрос.
            args: Дополнительные аргументы.
            kwargs: Дополнительные аргументы.

        Returns:
            Response: Ответ с сериализованными данными рецепта.

        Raises:
            exceptions.NotFound: Если рецепт не найден.
        """
        try:
            recipe = Recipe.objects.get(pk=kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise exceptions.NotFound
        Favorite.objects.create(recipe=recipe, user=request.user)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data)

    @favorite.mapping.delete
    def unfavorite(self, request, *args, **kwargs):
        """
        Удаляет рецепт из избранного.

        Args:
            request: Текущий запрос.
            args: Дополнительные аргументы.
            kwargs: Дополнительные аргументы.

        Returns:
            Response: Ответ с сериализованными данными рецепта.

        Raises:
            exceptions.NotFound: Если рецепт или избранное не найдены.
        """
        try:
            recipe = Recipe.objects.get(pk=kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise exceptions.NotFound
        try:
            favorite = Favorite.objects.get(recipe=recipe, user=request.user)
        except Favorite.DoesNotExist:
            raise exceptions.NotFound
        favorite.delete()
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """
        Скачивает список ингредиентов из корзины покупок в виде PDF.

        Args:
            request: Текущий запрос.

        Returns:
            HttpResponse: Ответ с PDF-файлом.
        """
        queryset = ShoppingCart.objects.filter(user=request.user)
        result = defaultdict(dict)
        for item in queryset:
            recipe = item.recipe
            ingredients_amounts = (
                recipe.amount_ingredients.all().select_related('ingredient')
            )
            for ingredient_amount in ingredients_amounts:
                ingredient = ingredient_amount.ingredient.name
                amount = ingredient_amount.amount
                unit = ingredient_amount.ingredient.measurement_unit
                if ingredient in ingredients_amounts:
                    if unit in ingredients_amounts[ingredient]:
                        result[ingredient][unit] += amount
                    else:
                        result[ingredient][unit] = amount
                else:
                    result[ingredient] = {unit: amount}
        buffer = BytesIO()
        pdfmetrics.registerFont(
            TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf', 'UTF-8'))
        c = canvas.Canvas(buffer, pagesize=letter)
        y = 750
        x_offset = 50
        c.setFont('DejaVuSans', 12,)
        c.drawString(x_offset, y, 'Список ингредиентов в корзине:')
        for ingredient, quantities in result.items():
            y -= 20
            c.drawString(x_offset, y, f'{ingredient}:')
            for unit, amount in quantities.items():
                y -= 15
                c.drawString(x_offset + 20, y, f'- {amount} {unit}')
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="ingredients.pdf"'
        response.write(pdf)
        return response

    @action(['post'], detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        """
        Добавляет рецепт в корзину покупок.

        Args:
            request: Текущий запрос.
            args: Дополнительные аргументы.
            kwargs: Дополнительные аргументы.

        Returns:
            Response: Ответ с сериализованными данными рецепта.
        
        Raises:
            exceptions.NotFound: Если рецепт не найден.
        """
        try:
            recipe = Recipe.objects.get(pk=kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise exceptions.NotFound
        ShoppingCart.objects.create(recipe=recipe, user=request.user)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, *args, **kwargs):
        """
        Удаляет рецепт из корзины покупок.

        Args:
            request: Текущий запрос.
            args: Дополнительные аргументы.
            kwargs: Дополнительные аргументы.

        Returns:
            Response: Ответ с сериализованными данными рецепта.
        
        Raises:
            exceptions.NotFound: Если рецепт или корзина покупок не найдены.
        """
        try:
            recipe = Recipe.objects.get(pk=kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise exceptions.NotFound
        try:
            shopping_cart = ShoppingCart.objects.get(recipe=recipe,
                                                     user=request.user)
        except ShoppingCart.DoesNotExist:
            raise exceptions.NotFound
        shopping_cart.delete()
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data)
