from django.contrib import admin
from .models import UserProfile, Post, Tag, PostImage

admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(PostImage)
