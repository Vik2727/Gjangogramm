from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.user_login, name='user_login'),
]
