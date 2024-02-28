from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.views import View
from PIL import Image
from io import BytesIO
import re

from djangogrammapp import settings
from .forms import UserProfileForm, PostForm
from main.models import UserProfile, Post, Tag, PostImage


class UserView(View):
    @method_decorator(login_required)
    def get(self, request):
        user_profile, created = UserProfile.objects.get_or_create(username=request.user)
        posts = Post.objects.all().order_by('-created_at')

        return render(request, 'user/user.html', {'user_data': user_profile, 'posts': posts})


class UserProfileView(View):
    @method_decorator(login_required)
    def get(self, request, user_post_id):
        user_profile, created = UserProfile.objects.get_or_create(username=request.user)
        user_data_post = UserProfile.objects.get(id=user_post_id)
        user_posts = Post.objects.filter(user=user_data_post).order_by('-created_at')
        is_subscribed = user_profile.is_subscribed_to(user_data_post)

        subscribers = user_data_post.subscribers.all()
        subscriptions = user_data_post.subscriptions.all()

        unique_tags = set()
        for post in user_posts:
            unique_tags.update(post.tags.all())

        context = {
            'user_data': user_profile,
            'user_data_post': user_data_post,
            'user_posts': user_posts,
            'is_subscribed': is_subscribed,
            'subscribers': subscribers,
            'subscriptions': subscriptions,
            'unique_tags': unique_tags
        }

        return render(request, 'user/user_profile.html', context)


class EditProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        user_profile, created = UserProfile.objects.get_or_create(username=request.user)
        form = UserProfileForm(instance=user_profile)
        return render(request, 'user/edit_profile.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        user_profile, created = UserProfile.objects.get_or_create(username=request.user)
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            user_profile.first_name = form.cleaned_data['first_name'].lower()
            user_profile.last_name = form.cleaned_data['last_name'].lower()

            avatar = form.cleaned_data['avatar']
            max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

            if avatar.size > max_size_bytes:
                post_processing_view = PostProcessingView()
                avatar = post_processing_view.resize_image(avatar, max_size_bytes)

            user_profile.avatar = avatar

            user_profile.save()

            request.user.first_name = user_profile.first_name
            request.user.last_name = user_profile.last_name
            request.user.save()

            return redirect('user')
        else:
            return render(request, 'user/edit_profile.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')


class PostProcessingView(View):
    def resize_image(self, image, max_size_bytes):
        thumbnail_size = settings.IMAGE_THUMBNAIL_SIZE
        with Image.open(image) as img:
            img.thumbnail(thumbnail_size)
            output = BytesIO()
            img.save(output, format='JPEG')
            return InMemoryUploadedFile(
                output, None, image.name, 'image/jpeg', output.getbuffer().nbytes, None
            )

    def post(self, request, *args, **kwargs):
        post = kwargs.get('post')
        tags = kwargs.get('tags')
        images = kwargs.get('images')

        post.save()

        for tag in tags:
            tag_instance, created = Tag.objects.get_or_create(name=tag.strip())
            post.tags.add(tag_instance)

        existing_tags = set(post.tags.values_list('name', flat=True))
        tags_to_remove = existing_tags - set(tags)
        Tag.objects.filter(name__in=tags_to_remove).delete()

        for image in images:
            max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

            if image.size > max_size_bytes:
                image = self.resize_image(image, max_size_bytes)

            post_instance = PostImage.objects.create(image=image)
            post.image.add(post_instance)

        post.save()

        return redirect('user')


class PostMixin(FormView):
    model = Post
    form_class = PostForm

    def get_request(self):
        return self.request if hasattr(self, 'request') else self.kwargs.get('request')

    def form_valid(self, form):
        user_profile = self.get_request().user.userprofile
        post = form.save(commit=False)
        post.user = user_profile
        caption = form.cleaned_data.get('caption')
        tags = re.findall(r'#\w+', caption)
        images = self.get_request().FILES.getlist('image')

        PostProcessingView.as_view()(self.get_request(), post=post, tags=tags, images=images)

        form.save_m2m()
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CreatePostView(PostMixin, CreateView):
    template_name = 'user/create_post.html'

    def get_context_data(self, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(username=self.request.user)
        context = super().get_context_data(**kwargs)
        context['user_data'] = user_profile
        context['post_form'] = context['form']
        return context

    def get_success_url(self):
        return reverse_lazy('user')


@method_decorator(login_required, name='dispatch')
class EditPostView(PostMixin, UpdateView):
    template_name = 'user/edit_post.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(username=self.request.user)
        context = super().get_context_data(**kwargs)
        context['user_data'] = user_profile
        context['post_form'] = context['form']
        return context

    def get_success_url(self):
        return reverse_lazy('user')


@method_decorator(login_required, name='dispatch')
class DeletePostView(DeleteView):
    model = Post
    template_name = 'user/delete_post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(username=self.request.user)
        context = super().get_context_data(**kwargs)
        context['user_data'] = user_profile
        return context

    def get_success_url(self):
        return reverse_lazy('user')


class PostsByTagView(View):
    def get(self, request, tag, user_post_id):
        user_profile, created = UserProfile.objects.get_or_create(username=request.user)
        user_data_post = UserProfile.objects.get(id=user_post_id)
        posts = Post.objects.filter(tags__name__iexact=tag).order_by('-created_at')

        context = {'user_data': user_profile,
                   'user_data_post': user_data_post,
                   'posts': posts,
                   'tag': tag}
        return render(request, 'user/posts_by_tag.html', context)


class ToggleLikeView(View):
    @method_decorator(login_required)
    def post(self, request, post_id, action):
        user_profile = request.user.userprofile
        post = get_object_or_404(Post, id=post_id)

        if action == 'like':
            post.likes.add(user_profile)
            post.dislikes.remove(user_profile)
        elif action == 'dislike':
            post.dislikes.add(user_profile)
            post.likes.remove(user_profile)

        return JsonResponse({'post_id': post_id, 'likes': post.total_likes(), 'dislikes': post.total_dislikes()})


class SubscribeToggleView(View):
    def post(self, request, user_post_id, action):
        user_profile, created = UserProfile.objects.get_or_create(username=request.user)
        user_data_post = UserProfile.objects.get(id=user_post_id)
        is_subscribed = user_profile.is_subscribed_to(user_data_post)

        if action == 'unsubscribe':
            user_profile.subscriptions.remove(user_data_post)
        else:
            user_profile.subscriptions.add(user_data_post)

        subscribers_count = user_data_post.subscribers.count()

        return JsonResponse({'is_subscribed': is_subscribed, 'subscribers_count': subscribers_count})
