from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='user'),
    path('user_profile/<int:user_post_id>/', views.UserProfileView.as_view(), name='user_profile'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path('edit_post/<int:post_id>/', views.EditPostView.as_view(), name='edit_post'),
    path('delete_post/<int:post_id>/', views.DeletePostView.as_view(), name='delete_post'),
    path('posts_by_tag/<str:tag>.<int:user_post_id>/', views.PostsByTagView.as_view(), name='posts_by_tag'),
    path('toggle_like/<int:post_id>/<str:action>/', views.ToggleLikeView.as_view(), name='toggle_like'),
    path('user_profile/<int:user_post_id>/subscribe_toggle/<str:action>/', views.SubscribeToggleView.as_view(), name='subscribe_toggle')
]
