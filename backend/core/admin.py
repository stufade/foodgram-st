from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import mark_safe
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, ShopCart,
                     Subscription)

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'full_name', 'email', 'avatar_preview',
        'recipe_count', 'subscription_count', 'subscriber_count'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

    @admin.display(description="ФИО")
    def full_name(self, obj):
        return obj.full_name()

    @admin.display(description="Аватар", ordering="avatar")
    @mark_safe
    def avatar_preview(self, obj):
        if obj.avatar:  # без этого выдаёт ошибку!
            return (
                f'<img src="{obj.avatar.url}" width="50" height="50" '
                'style="border-radius:50%;">'
            )

    @admin.display(description="Рецептов")
    def recipe_count(self, obj):
        return obj.recipes.count()

    @admin.display(description="Подписок")
    def subscription_count(self, obj):
        return obj.subscribers.count()

    @admin.display(description="Подписчиков")
    def subscriber_count(self, obj):
        return obj.authors.count()


class IngredientResource(ModelResource):
    class Meta:
        model = Ingredient
        exclude = ('id',)
        skip_first_row = True
        encoding = 'utf-8-sig'
        import_mode = 1
        import_id_fields = []


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'favorites_count', 'ingredients_list', 'image_preview'
    )
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('author', 'cooking_time')
    inlines = [RecipeIngredientInline]

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Ингредиенты')
    @mark_safe
    def ingredients_list(self, obj):
        return "<br>".join((
            f'{ri.ingredient.name} — {ri.amount} '
            f'{ri.ingredient.measurement_unit}')
            for ri in obj.recipe_ingredients.all())

    @admin.display(description="Изображение", ordering='image')
    @mark_safe
    def image_preview(self, obj):
        return (
            f'<img src="{obj.image.url}" '
            'style="max-height: 100px;'
            'max-width: 100px; border-radius: 10px;" />'
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Favorite, ShopCart)
class UserRecipeRelationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'author__username')