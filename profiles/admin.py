from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import Account, Comment, Post


# Register your models here.

class AccountAdmin(UserAdmin):
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Motto'),
         {
             'fields': ('motto',)
         }
         ),
        (_('Permissions'),
         {
             'fields': ('is_superuser',)
         }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
    )

    list_display = ('email', 'username', 'date_created', 'date_updated', 'is_superuser')
    search_fields = ('email', 'username')
    list_filter = ('is_superuser',)
    ordering = ('username', 'date_created')


class PostAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('author', 'title', 'statement', ('reported', 'trending', 'controversial'))
        }),
    )

    list_display = ('title', 'author', 'date_created', 'last_edited')
    ordering = ('title', 'date_created', 'last_edited')


class CommentAdmin(admin.ModelAdmin):
    fields = ('author', 'posted_to', 'statement', 'votes', 'upvotes', 'downvotes')

    list_display = ('author', 'date_created', 'last_edited')
    ordering = ('author', 'date_created', 'last_edited')


admin.site.register(Account, AccountAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
