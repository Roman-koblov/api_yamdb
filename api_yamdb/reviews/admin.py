from django.contrib import admin

from .models import Category, Comment, Review, Title, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'role'
    )
    list_editable = ('role',)
    list_filter = ('role',)
    search_fields = ('username',)
    empty_value_display = '-пусто-'


admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Title)
admin.site.register(Category)
