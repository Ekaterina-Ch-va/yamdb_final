from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import filters, mixins, status, viewsets
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination
)
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.models import Q
from api.filters import FilterTitle
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitlePostSerializer,
    TitleSerializer,
    CommentSerializer,
    ReviewSerializer,
    UserSerializer,
    UserProfileSerializer,
    SingUpSerializer,
    SendUserTokenSerializer
)
from api.permissions import (
    IsAuthorHighUserOrReadOnly, IsAdmin, IsAdminOrReadOnly
)
from reviews.models import Category, Comment, Genre, Review, Title, User


class ReviewViewSet(viewsets.ModelViewSet):
    """Отзывы"""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorHighUserOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        serializer.save(title=title, author=self.request.user)

    def perform_update(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        review_id = self.kwargs.get('pk')
        author = Review.objects.get(pk=review_id).author
        serializer.save(title_id=title.id, author=author)


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии"""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorHighUserOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        serializer.save(review=review, author=self.request.user)

    def perform_update(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        comment_id = self.kwargs.get('pk')
        author = Comment.objects.get(pk=comment_id).author
        serializer.save(review_id=review.id, author=author)


class CustomViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    """Произведение"""
    queryset = Title.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = FilterTitle
    search_fields = ('name', 'category__slug', 'genre__slug', 'year')
    ordering_fields = ('name', '-year')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitlePostSerializer

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            queryset = (Title.objects.prefetch_related('reviews').all().
                        annotate(rating=Avg('reviews__score')))
            return queryset
        return Title.objects.all()


class GenreViewSet(CustomViewSet):
    """Жанр"""
    queryset = Genre.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    search_fields = ('name', 'slug')
    filterset_fields = ('name', 'slug')


class CategoryViewSet(CustomViewSet):
    """Категория"""
    queryset = Category.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ('name', 'slug')
    search_fields = ('name', 'slug')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = [IsAdmin | IsAdminUser, ]
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete', 'patch', 'list']

    @action(
        detail=False,
        url_path='me',
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,)
    )
    def user_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserProfileSerializer(

                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SingUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SingUpSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        serializer = SingUpSerializer(data=request.data)
        try:
            user = User.objects.get(
                username__iexact=request.data.get('username')
            )
            data = serializer.initial_data
            if User.objects.filter(
                Q(username=data.get('username'))
                & ~Q(email__iexact=data.get('email'))
            ):
                raise ValidationError(
                    'Полученный email или username уже используется.'
                )
        except User.DoesNotExist:
            serializer.is_valid(raise_exception=True)
            user = User.objects.create(**serializer.validated_data)
            data = serializer.data
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='confirmation_code api_yandb',
            message=confirmation_code,
            from_email=None,
            recipient_list=(user.email,),
            fail_silently=False,
        )
        return Response(data, status=status.HTTP_200_OK)


class SendUserTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SendUserTokenSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        serializer = SendUserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return Response({'username': 'Нет такого пользователя'},
                            status=status.HTTP_404_NOT_FOUND)
        if default_token_generator.check_token(
            user, serializer.validated_data["confirmation_code"]
        ):
            jwt_token = AccessToken.for_user(user)
            return Response({'jwt_token': str(jwt_token)},
                            status=status.HTTP_201_CREATED)
        return Response({'Код подтверждения не действителен'},
                        status=status.HTTP_400_BAD_REQUEST)
