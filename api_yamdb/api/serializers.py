from rest_framework import serializers
from django.db.models import Avg
from django.utils.text import slugify

from reviews.models import (
    User,
    Category,
    Genre,
    Review,
    Title,
    Comment
)


class UserSerializer(serializers.ModelSerializer):
    
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
        read_only_fields = ('role',)


class AdminUserSerializer(serializers.ModelSerializer):
    
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


class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )

    def validate(self, data):
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Вы уже зарегестрированы!'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Это имя занято!'
            )
        return data


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True
    )
    confirmation_code = serializers.CharField(
        required=True
    )

    def validate(self, data):
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Имя занято'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'email уже используется'
            )
        return data

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    pub_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'text', 'score', 'author', 'pub_date']
        read_only_fields = ['id', 'author', 'pub_date']

    def get_pub_date(self, obj):
        return obj.pub_date.strftime('%Y-%m-%d')

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Score must be between 1 and 10.")
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


class GenreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Genre
        fields = ['name', 'slug']

    def create(self, validated_data):
        slug = validated_data.get('slug') or slugify(validated_data['name'])
        i = 1
        while Genre.objects.filter(slug=slug).exists():
            slug = f"{slugify(validated_data['name'])}-{i}"
            i += 1
        validated_data['slug'] = slug
        return super().create(validated_data)


class TitleSerializer(serializers.ModelSerializer):
    genre = genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    ) 
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
        return rating if rating is not None else None
    
    def to_representation(self, instance):
        self.fields['category'] = CategorySerializer()
        return super().to_representation(instance)
    
    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            title.genre.add(genre)
        return title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
