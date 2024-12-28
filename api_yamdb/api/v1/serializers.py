from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.v1.constants import (EMAIL_MAX_LENGTH, MAX_SCORE, MIN_SCORE,
                              USERNAME_MAX_LENGTH)
from api_yamdb.settings import FROM_EMAIL
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import ValidateUsername


class UserSerializer(serializers.ModelSerializer, ValidateUsername):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SingupSerializer(serializers.Serializer, ValidateUsername):

    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=[ValidateUsername()]
    )
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH
    )

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            from_email=FROM_EMAIL,
            message=f'{confirmation_code}',
            recipient_list=[user.email]
        )
        return user

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        if User.objects.filter(username=username, email=email).exists():
            return data
        if (
            User.objects.filter(username=username).exists()
            or User.objects.filter(email=email).exists()
        ):
            raise serializers.ValidationError()
        return data


class TokenSerializer(serializers.Serializer, ValidateUsername):

    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH
    )
    confirmation_code = serializers.CharField(required=True)

    def validate(self, validated_data):
        user = get_object_or_404(
            User,
            username=validated_data['username']
        )
        if default_token_generator.check_token(
                user,
                validated_data['confirmation_code']
        ):
            return validated_data
        raise serializers.ValidationError(
            'Confirmation_code неверный!'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Review
        fields = ['id', 'text', 'score', 'author', 'pub_date']

    def validate_score(self, value):
        if not MIN_SCORE <= value <= MAX_SCORE:
            raise serializers.ValidationError(
                f"Score must be between {MIN_SCORE} and {MAX_SCORE}."
            )
        return value

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        user = request.user

        if request.method == 'POST':
            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError(
                    "Вы уже оставили отзыв на это произведение."
                )
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        search_fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name', 'slug']
        search_fields = ['name']


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=True,
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['category'] = CategorySerializer()
        self.fields['genre'] = GenreSerializer(many=True)
        return super().to_representation(instance)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
