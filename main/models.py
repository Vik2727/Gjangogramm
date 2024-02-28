from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField


class UserProfile(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = CloudinaryField('avatar_image', folder='avatar_image', blank=True, null=True)
    subscriptions = models.ManyToManyField('self', symmetrical=False, related_name='subscribers', blank=True)
    objects = models.Manager()

    class Meta:
        app_label = 'main'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username.username}'

    def is_subscribed_to(self, other_user_profile):
        return self.subscriptions.filter(pk=other_user_profile.pk).exists()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            username=instance,
            first_name=instance.first_name,
            last_name=instance.last_name
        )
    else:
        instance.userprofile.save()


class Tag(models.Model):
    name = models.CharField(max_length=50)
    objects = models.Manager()


class PostImage(models.Model):
    image = CloudinaryField('post_image', folder='post_image', null=True)
    objects = models.Manager()


class Post(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    image = models.ManyToManyField(PostImage, related_name='post_images')
    likes = models.ManyToManyField(UserProfile, related_name='post_likes', blank=True)
    dislikes = models.ManyToManyField(UserProfile, related_name='post_dislikes', blank=True)
    objects = models.Manager()

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()
