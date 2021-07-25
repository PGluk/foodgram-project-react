from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django_base64field.fields import Base64Field

User = get_user_model()


class Ingredient(models.Model):
    class Unit(models.TextChoices):
        GRAM = 'gram', 'г'
        KILOGRAM = 'kilogram', 'кг'

    name = models.CharField(
        max_length=20,
        null=False,
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=8,
        choices=Unit.choices,
        default=Unit.GRAM,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit', ],
                name='unique_recipe_ingredient')
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20, null=False)
    color = models.CharField(max_length=8, null=False)
    slug = models.SlugField(null=False)

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False
    )
    name = models.CharField(
        null=False,
        blank=False,
        max_length=30,
        verbose_name='Название рецепта'
    )
    image = Base64Field(
        max_length=900000,
        blank=True,
        null=True
    )
    text = models.TextField(
        max_length=128,
        null=False,
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredients')
    tags = models.ManyToManyField(Tag, through='ReceiptTags')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ('name', 'pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.author}: {self.name}'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name='Количество ингредиента'
    )


class ReceiptTags(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class Follow(models.Model):
    user = models.ForeignKey(
        User, verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User, verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name='Дата создания'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} following {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь', )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='Рецепт', )
    added_date = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} added {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )]

    def __str__(self):
        return f'{self.user} added {self.recipe}'
