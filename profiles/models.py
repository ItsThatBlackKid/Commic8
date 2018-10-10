from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from location_field.models.spatial import LocationField
from rest_framework.authtoken.models import Token

import random
import string


class AccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):

        if not email:
            raise ValueError('Users must have a valid email address.')

        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username.')

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **kwargs):
        kwargs.setdefault('is_superuser', False)

        return self._create_user(self, email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_superuser') is not True:
            raise ValueError("Superusers must have is_superuser=True")

        return self._create_user(email, password, **kwargs)


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=200, unique=True, primary_key=True)
    profile_pic = models.ImageField(
        default=None,
        upload_to=lambda instance, filename: 'images/{}/profile_pic'.format(instance.username),

    )

    is_superuser = models.BooleanField(default=False)

    # a personalised message to describe the user
    motto = models.CharField(max_length=180, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = AccountManager()

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        # TODO match the object with permission
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


# give users tokens
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Abstract Editable Model
class Editable(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Abstract Votable Model
class Votable(models.Model):
    votes = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def update_votes(self):
        self.votes = self.upvotes - self.downvotes

    def upvote(self):
        self.upvotes += 1
        self.save()

    def downvote(self):
        self.downvotes += 1
        self.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.update_votes()
        super(Votable, self).save(force_insert=force_insert, force_update=force_update,
                                  using=using, update_fields=update_fields)


class UniqueIdentifiers(models.Model):
    uid = models.CharField(max_length=11)
    is_used = models.BooleanField(default=False)


class Report(models.Model):
    reason = models.TextField()
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reports')


class Community(models.Model):
    suburb = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    location = LocationField(based_fields=['suburb', 'city', 'zipcode'])


class Post(Votable, Editable):
    title = models.CharField(max_length=180)
    statement = models.TextField(default=None)
    author = models.ForeignKey('Account', on_delete=models.SET_NULL, related_name='posts', null=True, blank=True, )
    # community = models.ForeignKey('Community', on_delete=models.SET_NULL, related_name='posts', null=False)

    post_url = models.SlugField(null=True, default=None, unique=True)

    reported = models.BooleanField(default=False)
    controversial = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)
    locale_is_uni = models.BooleanField(default=False)

    def __unicode__(self):
        return self.pk

    def __str__(self):
        return self.title

    def edit(self, **kwargs):
        self.is_edited = True
        self.statement = kwargs['statement']

    def set_status(self, **kwargs):
        self.reported = kwargs.get('reported', self.reported)
        self.controversial = kwargs.get('controversial', self.controversial)
        self.trending = kwargs.get('trending', self.trending)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk:
            count = UniqueIdentifiers.objects.aggregate(count=Count('id'))['count']
            rand_index = random.randint(0, count - 1)
            p_uid = UniqueIdentifiers.objects.filter(is_used=False)[rand_index]
            p_uid.is_used = True
            self.post_url = p_uid.uid

        super(Post, self).save()


class Comment(Votable, Editable):
    posted_to = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('Account', on_delete=models.SET_NULL, related_name='comments', null=True)
    statement = models.TextField()

    def __unicode__(self):
        return self.pk

    def edit(self, **kwargs):
        self.is_edited = True
        self.statement = kwargs['statement']


class Message(Editable):
    author = models.ForeignKey('Account', on_delete=models.SET_NULL, related_name='messages_sent', null=True)
    body = models.TextField()
