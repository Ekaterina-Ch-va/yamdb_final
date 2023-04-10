from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, SendUserTokenViewSet, SingUpViewSet,
                    TitleViewSet, UserViewSet)

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'auth/signup', SingUpViewSet, basename='singup')
router.register(r'auth/token', SendUserTokenViewSet, basename='sendtoken')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'token/',
        TokenObtainPairView.as_view(),
        name='sendtoken'
    ),
]
