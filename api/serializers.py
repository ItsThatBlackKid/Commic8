from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers
from profiles.models import Account, Post, Comment, Message


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), many=False, allow_null=True)
    posted_to = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), many=False, allow_null=False)

    def edit(self, instance):
        instance.edit(**self.validated_data)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'posted_to', 'statement', 'votes', 'upvotes', 'downvotes', 'date_created',
                  'is_edited', 'last_edited')
        read_only_fields = ('date_created', 'last_edited', 'is_edited', 'votes', 'upvotes', 'downvotes')


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), many=False, allow_null=True,
                                                allow_empty=True, required=False)
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'statement', 'votes', 'upvotes', 'downvotes', 'date_created',
                  'is_edited', 'last_edited', 'comments', 'post_url')
        read_only_fields = ('date_created', 'date_edited', 'votes', 'comments', 'is_edited', 'date_created',
                            'last_edited', 'votes', 'upvotes', 'downvotes', 'id', 'post_url')


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), many=False, allow_null=True,
                                                allow_empty=True, required=False)

    class Meta:
        model = Message
        fields = ('id', 'author', 'body', 'date_created')
        read_only_fields = ('date_created', 'id')


class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    posts = PostSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, required=False)

    def create(self, validated_data):
        user = super(AccountSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        setattr(instance, 'username', self.validated_data.get('username', instance.username))
        setattr(instance, 'motto', self.validated_data.get('username', instance.motto))
        instance.save()

        password = self.validated_data.get('password', None)
        confirm_password = self.validated_data.get('password2', None)

        if password and confirm_password and password == confirm_password:
            instance.set_password(password)
            instance.save()

        update_session_auth_hash(self.context.get('request'), instance)

        return instance

    class Meta:
        model = Account
        fields = ('profile_pic', 'username', 'email', 'password', 'motto', 'date_created',
                  'date_updated', 'last_login', 'posts', 'comments')
        read_only_fields = ('created_at', 'last_updated', 'last_login', 'posts', 'comments')
