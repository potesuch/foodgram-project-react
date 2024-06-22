from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, AmountIngredient, ShoppingCart,
                     Favorite)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Административная панель для управления тегами.
    """
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Административная панель для управления ингредиентами.
    """
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Административная панель для управления рецептами.
    """
    list_display = ('name', 'author', 'get_tags')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author')

    def get_queryset(self, request):
        """
        Получает набор запросов с предзагруженными тегами.
        """
        return super().get_queryset(request).prefetch_related('tags')

    @admin.display(description='tags')
    def get_tags(self, obj):
        """
        Возвращает список тегов рецепта.
        """
        return ', '.join(tag.name for tag in obj.tags.all())


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    """
    Административная панель для управления количеством ингредиентов в рецептах.
    """
    list_display = ('get_ingredient_name', 'get_recipe_name', 'amount')
    search_fields = ('get_ingredient_name', 'get_recipe_name')

    @admin.display(description='ingredient name')
    def get_ingredient_name(self, obj):
        """
        Возвращает название ингредиента.
        """
        return obj.ingredient.name

    @admin.display(description='recipe name')
    def get_recipe_name(self, obj):
        """
        Возвращает название рецепта.
        """
        return obj.recipe.name


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Административная панель для управления корзинами покупок.
    """
    list_display = ('get_recipe_name', 'user')
    search_fields = ('get_recipe_name', 'user')

    @admin.display(description='ingredient name')
    def get_recipe_name(self, obj):
        """
        Возвращает название рецепта.
        """
        return obj.recipe.name


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Административная панель для управления избранными рецептами.
    """
    list_display = ('get_recipe_name', 'user')
    search_fields = ('get_recipe_name', 'user')

    @admin.display(description='ingredient name')
    def get_recipe_name(self, obj):
        """
        Возвращает название рецепта.
        """
        return obj.recipe.name
