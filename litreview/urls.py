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
from django.urls import path
from users.views import UserLoginView, UserSignUpView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', UserLoginView.as_view(template_name='users/loginpage_html'),
         name='login-page'),  # This line includes the login URL for the users app
    path('', UserSignUpView.as_view(), 
         name='signup-page'),  # This line includes the signup URL for the users app 
]
