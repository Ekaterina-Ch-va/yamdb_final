import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def validate_year(value):
    year_today = dt.datetime.now().year
    if value > year_today:
        raise ValidationError(
            'Введен некорректный год создания произведения!',
            params={'value': value},
        )


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]
    bio = models.TextField(verbose_name='Биография', blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(
        max_length=15,
        choices=ROLES,
        default=USER
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    """Модель категория произведения."""
    name = models.CharField(
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанр произведения."""
    name = models.CharField(
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель самого произведения."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения.'
    )
    description = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='Краткое содержание.'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='genres'
    )
    year = models.IntegerField(
        default=0,
        validators=[validate_year],
        verbose_name='Год создания',
    )

    class Meta:
        ordering = ('category', 'name')
        verbose_name = 'Произведение.'
        verbose_name_plural = 'Произведения.'

    def __str__(self):
        return f'{self.name}, {self.category}, {str(self.year)}'


class Review(models.Model):
    """Модель отзывов на произведения"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название произведения.'
    )
    text = models.TextField(verbose_name='Текст отзыва.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва.'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'Слишком маленькая оценка!'),
                    MaxValueValidator(10, 'Слишком большая оценка!')],
        verbose_name='Оценка.'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author'
            )
        ]
        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев к отзывам"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв.'
    )
    text = models.TextField(verbose_name='Текст комментария.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария.'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
