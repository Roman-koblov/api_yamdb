from django_filters import (CharFilter, FilterSet, ModelMultipleChoiceFilter,
                            NumberFilter)
from reviews.models import Genre, Title


class TitleFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    category = CharFilter(field_name='category__slug')
    genre = ModelMultipleChoiceFilter(
        field_name='genre__slug',
        to_field_name='slug',
        queryset=Genre.objects.all()
    )
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'year', 'name')
