from rest_framework import serializers

from reviews.models import (
    User,
    Category,
    Genre,
    Title
)

class AdminSerializer(serializers.ModelSerializer):
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

class NotAdminSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Genre
        fields = ['name', 'slug']


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = '__all__'
