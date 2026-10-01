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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from users.views import UserLoginView, UserSignUpView
from reviews.views import (
    BookView, BookCreate,
    ReviewCreate, ReviewUpdate, ReviewDelete,
    HomepageView, BookSearchView, UserSearchView,
    SearchRedirectView, ToggleFollowView, MyProfileView,
    UserProfileView)

APP_NAME = 'users', 'reviews'

urlpatterns = [
    path("admin/", admin.site.urls),
    path('homepage/', HomepageView.as_view(), name='home-page'),
    path('search/', SearchRedirectView.as_view(), name='search-dispatch'),

    path('profile/', MyProfileView.as_view(), name='my-profile'),
    path('signup/', UserSignUpView.as_view(), name='signup-page'),
    path('login/', UserLoginView.as_view(), name='login-page'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('book/search/', BookSearchView.as_view(), name='book-search'),

    path('users/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('users/<str:username>/follow/', ToggleFollowView.as_view(), name='toggle-follow'),

    path('book/add/', BookCreate.as_view(), name='book-create'),
    path('book/<int:book_id>/', BookView.as_view(), name='book-review'),
    path('book/<int:book_id>/review/add/', ReviewCreate.as_view(), name='review-create'),
    path('book/<int:book_id>/review/update/', ReviewUpdate.as_view(), name='review-update'),
    path('book/<int:book_id>/review/delete/', ReviewDelete.as_view(), name='review-delete'),
]

# builds the image rendering path for you (dev only configuration for image rendering)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
