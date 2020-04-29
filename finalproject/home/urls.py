from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name='home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    # path('home', views.HomeView.as_view() ),
]
