from django.urls import resolve, reverse, reverse_lazy
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO

from user import views
from user.views import PostMixin, DeletePostView, CreatePostView, EditPostView, PostProcessingView
from main.models import Post, Tag, PostImage


class TestUserUrls(TestCase):
    def test_user_url_resolves(self):
        resolved_view = resolve('/user/')
        self.assertEqual(resolved_view.func.view_class, views.UserView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'user')

    def test_user_profile_url_resolves(self):
        user_post_id = 1
        resolved_view = resolve(f'/user/user_profile/{user_post_id}/')
        self.assertEqual(resolved_view.func.view_class, views.UserProfileView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'user_profile')

    def test_edit_profile_url_resolves(self):
        resolved_view = resolve('/user/edit_profile/')
        self.assertEqual(resolved_view.func.view_class, views.EditProfileView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'edit_profile')

    def test_logout_user_url_resolves(self):
        resolved_view = resolve('/user/logout/')
        self.assertEqual(resolved_view.func.view_class, views.LogoutView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'logout')

    def test_create_post_url_resolves(self):
        resolved_view = resolve('/user/create_post/')
        self.assertEqual(resolved_view.func.view_class, views.CreatePostView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'create_post')

    def test_edit_post_url_resolves(self):
        post_id = 1
        resolved_view = resolve(f'/user/edit_post/{post_id}/')
        self.assertEqual(resolved_view.func.view_class, views.EditPostView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'edit_post')

    def test_delete_post_url_resolves(self):
        resolved_view = resolve('/user/delete_post/1/')
        self.assertEqual(resolved_view.func.view_class, views.DeletePostView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'delete_post')

    def test_posts_by_tag_url_resolves(self):
        user_post_id = 1
        tag = 'example_tag'
        resolved_view = resolve(f'/user/posts_by_tag/{tag}.{user_post_id}/')
        self.assertEqual(resolved_view.func.view_class, views.PostsByTagView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'posts_by_tag')

    def test_toggle_like_url_resolves(self):
        post_id = 1
        action = 'like'
        resolved_view = resolve(f'/user/toggle_like/{post_id}/{action}/')
        self.assertEqual(resolved_view.func.view_class, views.ToggleLikeView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'toggle_like')

    def test_subscribe_toggle_url_resolves(self):
        user_post_id = 1
        action = 'unsubscribe'
        resolved_view = resolve(f'/user/user_profile/{user_post_id}/subscribe_toggle/{action}/')
        self.assertEqual(resolved_view.func.view_class, views.SubscribeToggleView.as_view().view_class)
        self.assertEqual(resolved_view.url_name, 'subscribe_toggle')


class TestUserViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_data = {'username': 'testuseruser',
                          'first_name': 'testuser',
                          'last_name': 'useruser',
                          'password': 'testpassworduser',
                          'email': 'invalidemailuser'
                          }

        self.user_data_post = {'username': 'testuseruserpost',
                               'first_name': 'testuserpost',
                               'last_name': 'useruserpost',
                               'password': 'testpassworduserpost',
                               'email': 'invalidemailuserpost'
                               }

        self.user = User.objects.create_user(**self.user_data)
        self.user_post = User.objects.create_user(**self.user_data_post)

        self.user_profile = self.user.userprofile
        self.user_profile.bio = 'This is a test bio for user'
        self.user_profile.avatar = 'static/img/default_avatar.jpeg'
        self.user_profile.save()

        self.user_profile_post = self.user_post.userprofile
        self.user_profile_post.bio = 'This is a test bio for user'
        self.user_profile_post.avatar = 'static/img/default_avatar.jpeg'
        self.user_profile_post.save()

        self.tag = Tag.objects.create(name='Test Tag User')
        self.image = PostImage.objects.create(image='path/to/image.jpg')

        self.post = Post.objects.create(
            user=self.user_profile_post,
            caption='Test Caption User',
        )
        self.post.tags.add(self.tag)
        self.post.image.add(self.image)

    def test_user_view(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.get(reverse('user'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_profile.first_name, str(response.content))
        self.assertIn(self.user_profile.last_name, str(response.content))
        self.assertIn(self.post.caption, str(response.content))

    def test_user_profile_view(self):
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        url = reverse('user_profile', kwargs={'user_post_id': self.user_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_profile.first_name, str(response.content))
        self.assertIn(self.user_profile.last_name, str(response.content))
        self.assertIn(self.post.caption, str(response.content))

    def test_subscribe_toggle_view(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('subscribe_toggle', kwargs={'user_post_id': self.user_post.id,
                                                                        'action': 'subscribe'}))

        self.assertTrue(self.user.userprofile.is_subscribed_to(self.user_post.userprofile))

        response = self.client.post(reverse('subscribe_toggle', kwargs={'user_post_id': self.user_post.id,
                                                                        'action': 'unsubscribe'}))

        self.assertFalse(self.user.userprofile.is_subscribed_to(self.user_post.userprofile))

    def test_edit_profile_get(self):
        self.client.force_login(self.user)

        response_get = self.client.get(reverse('edit_profile'))
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'user/edit_profile.html')

        self.user_profile.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(self.user_profile.bio, 'This is a test bio for user')
        self.assertEqual(self.user_profile.first_name, 'testuser')
        self.assertEqual(self.user_profile.last_name, 'useruser')

        self.assertEqual(self.user.first_name, 'testuser')
        self.assertEqual(self.user.last_name, 'useruser')

        data_invalid = {'first_name': '', 'last_name': 'NewLastName', 'bio': 'New test bio'}
        response_invalid_form = self.client.post(reverse('edit_profile'), data_invalid)

        self.assertEqual(response_invalid_form.status_code, 200)
        self.assertIn('form', response_invalid_form.context)

    def test_edit_profile_post(self):
        url = reverse('edit_profile')
        response = self.client.post(url, {'first_name': 'John', 'last_name': 'Doe'})

        self.assertEqual(response.status_code, 302)

    def test_logout_user(self):
        self.client.force_login(self.user)

        request = RequestFactory().get(reverse('logout'))
        request.user = self.user

        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        request.user = AnonymousUser()
        self.assertIsInstance(request.user, AnonymousUser)

    def test_post_processing_resize_image(self):
        post_processing_view = PostProcessingView()

        image = Image.new('RGB', (800, 600))
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.name = 'test.jpg'
        image_file.seek(0)

        resized_image = post_processing_view.resize_image(image_file, max_size_bytes=1024 * 1024)
        self.assertTrue(isinstance(resized_image, InMemoryUploadedFile))
        self.assertLess(resized_image.size, 1024 * 1024)

    def test_post_mixin_get_request(self):
        mixin = PostMixin()
        request_mock = object()
        mixin.request = request_mock

        result = mixin.get_request()

        self.assertEqual(result, request_mock)

    def test_create_post_get_context_data(self):
        request = self.factory.get(reverse('create_post'))

        request.user = self.user
        view = CreatePostView.as_view()
        response = view(request, first_name=self.user_profile.first_name, last_name=self.user_profile.last_name)

        self.assertEqual(response.status_code, 200)

        self.assertIn('user_data', response.context_data)
        self.assertIn('post_form', response.context_data)

    def test_create_post_get_success_url(self):
        request = self.factory.get('create_post')
        request.user = self.user_post

        create_post_view = CreatePostView()
        create_post_view.request = request
        create_post_view.object = self.post

        success_url = create_post_view.get_success_url()
        expected_url = reverse_lazy('user')

        self.assertEqual(success_url, expected_url)

    def test_edit_post_get_context_data(self):
        request = self.factory.get(reverse('edit_post', kwargs={'post_id': self.post.id}))

        request.user = self.user
        edit_post_view = EditPostView.as_view()
        response = edit_post_view(request, post_id=self.post.id)

        self.assertEqual(response.status_code, 200)

        self.assertIn('user_data', response.context_data)
        self.assertIn('post_form', response.context_data)

        user_data = response.context_data['user_data']
        post_form = response.context_data['post_form']

        self.assertEqual(user_data, self.user_profile)
        self.assertEqual(post_form.instance, self.post)

    def test_edit_post_get_success_url(self):
        self.update_view = EditPostView()
        self.update_view.object = self.post

        success_url = self.update_view.get_success_url()
        expected_url = reverse_lazy('user')

        self.assertEqual(success_url, expected_url)

    def test_delete_post_get_context_data(self):
        request = self.factory.get(reverse('delete_post', kwargs={'post_id': self.post.id}))

        request.user = self.user
        view = DeletePostView.as_view()
        response = view(request, post_id=self.post.id)

        self.assertEqual(response.status_code, 200)
        self.assertIn('user_data', response.context_data)
        self.assertEqual(response.context_data['user_data'], self.user_profile)

    def test_delete_post_get_success_url(self):
        self.update_view = DeletePostView()
        self.update_view.object = self.post

        success_url = self.update_view.get_success_url()
        expected_url = reverse_lazy('user')

        self.assertEqual(success_url, expected_url)

    def test_posts_by_tag(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('posts_by_tag', kwargs={'tag': self.tag.name,
                                                                   'user_post_id': self.user_post.id}))

        self.assertEqual(response.status_code, 200)
        self.assertIn('user/posts_by_tag.html', [t.name for t in response.templates])
        self.assertEqual(response.context['posts'].count(), 1)
        self.assertEqual(response.context['posts'][0], self.post)
        self.assertEqual(response.context['tag'], self.tag.name)

    def test_toggle_like(self):
        self.client.force_login(self.user)

        # Like the post
        like_response = self.client.post(reverse('toggle_like', kwargs={'post_id': self.post.id,
                                                                        'action': 'like'}))

        self.assertEqual(like_response.status_code, 200)
        self.assertEqual(like_response.headers['content-type'], 'application/json')

        like_data = like_response.json()
        self.assertIn('post_id', like_data)
        self.assertIn('likes', like_data)
        self.assertIn('dislikes', like_data)
        self.assertEqual(like_data['post_id'], self.post.id)
        self.assertEqual(like_data['likes'], 1)
        self.assertEqual(like_data['dislikes'], 0)

        # Dislike the post
        dislike_response = self.client.post(reverse('toggle_like', kwargs={'post_id': self.post.id,
                                                                           'action': 'dislike'}))
        self.assertEqual(dislike_response.status_code, 200)
        self.assertEqual(dislike_response.headers['content-type'], 'application/json')

        dislike_data = dislike_response.json()
        self.assertIn('post_id', dislike_data)
        self.assertIn('likes', dislike_data)
        self.assertIn('dislikes', dislike_data)
        self.assertEqual(dislike_data['post_id'], self.post.id)
        self.assertEqual(dislike_data['likes'], 0)
        self.assertEqual(dislike_data['dislikes'], 1)

