from coreapi.exceptions import ParseError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, detail_route, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from profiles.models import Account, Post, Comment, Message
from .serializers import AccountSerializer, CommentSerializer, PostSerializer, MessageSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    max_page_size = 20


class AccountViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def create(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.create(validated_data=serializer.validated_data)
            return Response({
                "status": "CREATED",
                "message": "Account Created!",
            }, status=status.HTTP_201_CREATED)

        print("couldn't create")
        return Response({
            "status": "Invalid Data",
            "message": "Account could not be created with provided credentials"
        }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.update(validated_data=serializer.validated_data)
            return Response({
                "status": "UPDATED",
                "message": "Account has been updated"
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "Invalid Data",
            "message": "Account could not be created with provided credentials"
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class PostViewSet(viewsets.ModelViewSet):
    lookup_field = 'post_url'
    queryset = Post.objects.all().order_by('-votes', 'date_created')
    serializer_class = PostSerializer
    ordering_fields = ('votes', 'date_created')

    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=['POST'])
    @permission_classes((IsAuthenticated,))
    def upvote(self,request, **kwargs):
        post = get_object_or_404(Post, post_url=kwargs['post_url'])
        post.upvote()
        return Response({'votes': post.votes}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'])
    @permission_classes((IsAuthenticated,))
    def downvote(self,request, **kwargs):
        print(kwargs)
        post = get_object_or_404(Post, post_url=kwargs['post_url'])
        post.downvote()
        return Response({'votes': post.votes}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def get_posts_by_user(request, **kwargs):
    user = request.user
    if Account.objects.filter(id=user.id).exists():
        posts = user.posts.all()

        if not posts:
            return Response({
                "status": "NO POSTS",
                "message": "Oh, looks like you haven't made any posts"
            }, status=status.HTTP_204_NO_CONTENT)

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({
        "status": "REJECTED",
        "message": "User token was rejected"
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', ])
def get_post_comments(request, **kwargs):
    p_id = kwargs['id']
    print(p_id)
    if Post.objects.filter(id=p_id).exists():
        post = Post.objects.get(id=p_id)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({
        "message": "No comments found"
    })


class CommentViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class MessageViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
