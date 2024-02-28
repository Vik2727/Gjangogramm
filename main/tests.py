from django.contrib.admin.sites import site
from django.test import TestCase, Client
from django.urls import reverse, resolve

from main.models import UserProfile, User, Tag, PostImage, Post
from main.views import index, user_login


class TestMainAdmin(TestCase):
    def test_admin_registration(self):
        self.assertIn(UserProfile, site._registry)
        self.assertIn(Post, site._registry)
        self.assertIn(Tag, site._registry)
        self.assertIn(PostImage, site._registry)


class TestDataMain(TestCase):
    def setUp(self):
        self.user_data = {'username': 'testusermain',
                          'first_name': 'testmain',
                          'last_name': 'usermain',
                          'password': 'testpasswordmain',
                          'email': 'invalidemailmain'
                          }

        self.user = User.objects.create_user(**self.user_data)

        self.user_profile = self.user.userprofile
        self.user_profile.bio = 'This is a test bio for main'
        self.user_profile.avatar = 'static/img/default_avatar.jpeg'
        self.user_profile.save()

        self.tag = Tag.objects.create(name='Test Tag Main')
        self.image = PostImage.objects.create(image='path/to/image.jpg')

        self.post = Post.objects.create(
            user=self.user_profile,
            caption='Test Caption Main',
        )
        self.post.tags.add(self.tag)
        self.post.image.add(self.image)


class TestMainModels(TestDataMain):
    def test_create_user_profile(self):
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user_profile.first_name, 'testmain')
        self.assertEqual(self.user_profile.last_name, 'usermain')
        self.assertEqual(self.user_profile.bio, 'This is a test bio for main')
        self.assertEqual(self.user_profile.avatar, 'static/img/default_avatar.jpeg')
        self.assertEqual(str(self.user_profile), 'testusermain')

    def test_create_tag(self):
        self.assertEqual(self.tag.name, 'Test Tag Main')

    def test_create_image(self):
        self.assertEqual(self.image.image, 'path/to/image.jpg')

    def test_create_post(self):
        self.assertEqual(Post.objects.count(), 1)

        post = Post.objects.first()
        self.assertEqual(post.user, self.user_profile)
        self.assertEqual(post.caption, 'Test Caption Main')
        self.assertEqual(list(post.tags.all()), [self.tag])
        self.assertEqual(list(post.image.all()), [self.image])
        self.assertEqual(post.total_likes(), 0)
        self.assertEqual(post.total_dislikes(), 0)
        self.assertEqual(list(post.likes.all()), [])
        self.assertEqual(list(post.dislikes.all()), [])

        post.likes.add(self.user_profile)
        self.assertEqual(post.total_likes(), 1)
        self.assertEqual(list(post.likes.all()), [self.user_profile])

        post.dislikes.add(self.user_profile)
        self.assertEqual(post.total_dislikes(), 1)
        self.assertEqual(list(post.dislikes.all()), [self.user_profile])

    def test_total_likes_and_dislikes(self):
        self.assertEqual(self.post.total_likes(), 0)
        self.assertEqual(self.post.total_dislikes(), 0)

        self.post.likes.add(self.user_profile)
        self.assertEqual(self.post.total_likes(), 1)
        self.assertEqual(self.post.total_dislikes(), 0)

        self.post.dislikes.add(self.user_profile)
        self.assertEqual(self.post.total_likes(), 1)
        self.assertEqual(self.post.total_dislikes(), 1)


class TestMainUrls(TestDataMain):
    def test_home_url_resolves(self):
        resolved_view = resolve('/')
        self.assertEqual(resolved_view.func, index)
        self.assertEqual(resolved_view.url_name, 'home')

    def test_user_login_url_resolves(self):
        resolved_view = resolve('/login/')
        self.assertEqual(resolved_view.func, user_login)
        self.assertEqual(resolved_view.url_name, 'user_login')


class TestMainViews(TestDataMain):
    def test_index(self):
        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('main/index.html', [t.name for t in response.templates])

    def test_user_login_success(self):
        client = Client()
        response = client.post(reverse('user_login'), {'username': 'testusermain', 'password': 'testpasswordmain'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('user'))

    def test_user_login_failure(self):
        client = Client()
        response = client.post(reverse('user_login'), {'username': 'nonexistentuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid login credentials.", response.content)

    def test_user_login_get(self):
        client = Client()
        response = client.get(reverse('user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Invalid login credentials.', response.content)

