from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """
    Фильтр для ингредиентов, позволяющий фильтровать по имени.
    """
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для рецептов, позволяющий фильтровать по избранным рецептам, корзине покупок и тегам.
    """
    is_favorited = filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def is_favorited_filter(self, queryset, name, value):
        """
        Фильтр для избранных рецептов.

        Args:
            queryset: Исходный набор запросов.
            name: Имя фильтра.
            value: Значение фильтра.

        Returns:
            queryset: Отфильтрованный набор запросов.
        """
        if value and not self.request.user.is_anonymous:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """
        Фильтр для рецептов в корзине покупок.

        Args:
            queryset: Исходный набор запросов.
            name: Имя фильтра.
            value: Значение фильтра.

        Returns:
            queryset: Отфильтрованный набор запросов.
        """
        if value and not self.request.user.is_anonymous:
            return queryset.filter(in_shopping_carts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
