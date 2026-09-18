"""litreview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from users.views import UserLoginView, UserSignUpView, UserProfileView
from reviews.views import BookView
from django.contrib import admin
from django.urls import path

APP_NAME = 'users'

urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/', UserSignUpView.as_view(), name='signup-page'),
    path('users/login', UserLoginView.as_view(), name='login-page'),
    path('users/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('bookreview/<str:title>/', BookView.as_view(), name='book-review')
]
