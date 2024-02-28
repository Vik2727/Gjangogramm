from django.urls import path
from . import views


urlpatterns = [
    path('', views.registration, name='registration'),
    path('activate_account/', views.activate_account, name='activate_account')
]
