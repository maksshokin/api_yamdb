from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
)


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'bio')}),
        (
            'Permissions',
            {'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'role'
            )}
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')
    search_fields = ('username', 'email')
    list_editable = ('role',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'get_genres', 'description')
    list_filter = ('year', 'category', 'genre')
    search_fields = ('name', 'category__name', 'genre__name')
    autocomplete_fields = ('category',)
    filter_horizontal = ('genre',)

    @admin.display(description='Жанры')
    def get_genres(self, obj):
        return ', '.join(
            [genre.name for genre in obj.genre.all()]
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('pub_date', 'score')
    search_fields = ('title__name', 'author__username', 'text')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'pub_date', 'text')
    list_filter = ('pub_date',)
    search_fields = ('review__text', 'author__username', 'text')


admin.site.register(User, UserAdmin)
