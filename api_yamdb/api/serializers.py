from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_email, validate_username


class CategorySerializer(ModelSerializer):
    """Сериализатор для категории"""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(ModelSerializer):
    """Сериализатор для жанра"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(ModelSerializer):
    """Сериализатор для чтения произведения"""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'description',
                  'category', 'genre', 'year', 'rating',)


class TitlePostSerializer(serializers.ModelSerializer):
    """Сериализатор для публикации произведения"""
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only = ('id')

    def validate(self, data):
        title = self.context['view'].kwargs.get('title_id')
        author = self.context['view'].request.user
        if (
            self.context['view'].request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise serializers.ValidationError(
                'Вы уже писали отзыв к этому произведению!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only = ('id')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150, validators=[validate_username]
    )
    email = serializers.EmailField(max_length=254, validators=[validate_email])

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'bio', 'role')


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150, validators=[validate_username]
    )
    email = serializers.EmailField(max_length=254, validators=[validate_email])

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('username', 'role')


class SingUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150, validators=[validate_username]
    )
    email = serializers.EmailField(max_length=254, validators=[validate_email])

    class Meta:
        model = User
        fields = ('email', 'username')


class SendUserTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
