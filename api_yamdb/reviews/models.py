
import datetime
import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

ADMIN = 'admin'
MODERATOR = 'moderator'
JUST_USER = 'user'

ROLE_CHOICES = (
    (JUST_USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)
USERNAME_ME_ERROR = 'Username указан неверно! Нельзя указать username "me"'
INVALID_CHARACTER_ERR = ('Username указан неверно!'
                         'Можно использовать только латинские буквы,'
                         'цифры и @/./+/-/_')
REGEX = re.compile(r'^[\w.@+-]+\Z')


def username_validator(value):
    if value == 'me':
        raise ValidationError(
            USERNAME_ME_ERROR
        )
    if not REGEX.match(value):
        raise ValidationError(
            INVALID_CHARACTER_ERR
        )
    return value


def current_year():
    return datetime.date.today().year


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Пользователь',
        validators=[username_validator],
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Адрес электронной почты'
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=JUST_USER,
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True
    )
    code = models.IntegerField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return (self.role == ADMIN or self.is_staff)

    @property
    def is_moderator(self):
        return (self.role == MODERATOR)

    @property
    def is_user(self):
        return (self.role == JUST_USER)


class BaseClassCategoryandGenre(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)


class Category(BaseClassCategoryandGenre):

    class Meta(BaseClassCategoryandGenre.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseClassCategoryandGenre):

    class Meta(BaseClassCategoryandGenre.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.TextField(
        verbose_name='Название',
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[MaxValueValidator(current_year)]
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='title'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='title',
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class BaseClassReviewandComment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date', )


class Review(BaseClassReviewandComment):
    score = models.IntegerField(validators=[MaxValueValidator(10),
                                            MinValueValidator(1)])
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta(BaseClassReviewandComment.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]
        default_related_name = 'reviews'


class Comment(BaseClassReviewandComment):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments')

    class Meta(BaseClassReviewandComment.Meta):
        default_related_name = 'comments'
