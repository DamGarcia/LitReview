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
from users.views import UserLoginView, UserSignUpView, UserProfileView
from reviews.views import BookView, BookCreate

APP_NAME = 'users', 'reviews'

urlpatterns = [
    path("admin/", admin.site.urls),
    path('signup/', UserSignUpView.as_view(), name='signup-page'),
    path('login/', UserLoginView.as_view(), name='login-page'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('users/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('book/<int:id>/', BookView.as_view(), name='book-review'),
    path('book/add/', BookCreate.as_view(), name='book-create'),
]

# builds the image rendering path for you (dev only configuration for image rendering)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
