from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as drf_views
from rest_framework_swagger.views import get_swagger_view

from .views import PostViewSet, AccountViewSet, CommentViewSet, MessageViewSet

app_name = 'api'
router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
schema_view = get_swagger_view(title='Commic8 API')
urlpatterns = [
    path('', include(router.urls)),
    path('docs/', schema_view),
    path('auth/', drf_views.obtain_auth_token, name='auth'),
]
