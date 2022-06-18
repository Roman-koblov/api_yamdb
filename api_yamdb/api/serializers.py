import datetime
import re

from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from reviews.models import (Category, Comment, Genre, Review, Title, User,
                            username_validator)

USERNAME_ME_ERROR = 'Username указан неверно! Нельзя указать username "me"'
INVALID_CHARACTER_ERR = ('Username указан неверно!'
                         'Можно использовать только латинские буквы,'
                         'цифры и @/./+/-/_')
DOUBLE_REVIEW_ERROR = 'Нельзя писать второй ревью'
DOUBLE_USERNAME_ERROR = ('Указанный username используется с другой почтой')
DOUBLE_EMAIL_ERROR = ('Указанный email используется с другим'
                      'именем пользователя')
SCORE_ERROR = 'Оценкой может быть целое число от 1 до 10'
REGEX = re.compile(r'^[\w.@+-]+\Z')


def current_year():
    return datetime.date.today().year


class UsernameValidationMixin:

    def validate_username(self, value):
        return username_validator(value)


class AdminUserSerializer(UsernameValidationMixin,
                          serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class UserSerializer(AdminUserSerializer):

    class Meta(AdminUserSerializer.Meta):
        read_only_fields = ('role',)


class SignupSerializer(UsernameValidationMixin, serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150
    )
    email = serializers.EmailField(
        required=True,
        max_length=254
    )


class TokenSerializer(UsernameValidationMixin, serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_slug = 'slug'


class TitleSeraializer(serializers.ModelSerializer):
    year = serializers.IntegerField(
        validators=[MaxValueValidator(current_year)]
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = ('__all__',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(validators=[MaxValueValidator(10),
                                                 MinValueValidator(1)])

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        my_view = self.context['view']
        title = my_view.kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(
                DOUBLE_REVIEW_ERROR
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
