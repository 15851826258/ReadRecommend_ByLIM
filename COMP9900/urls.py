"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path
from COMP9900_LIM import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage),
    path('login/', views.index),
    path('index/', views.index),
    path('index/homepage/', views.homepage),
    path('regist/', views.regist),
    path('regist/homepage/', views.homepage),
    path('createCo/', views.createCollection),
    path('deleteCo/', views.deleteCollection),
    path('profile/', views.profileview),
    path('createCo/profile/', views.profileview),
    path('deleteCo/profile/', views.profileview),
    path('logout/', views.logout),
    path('search/', views.search),
    path('addBk2Co/', views.addBk2Co),
    path('deleteBk/', views.deleteBk),
    path('homepage/', views.homepage),
    path('Bkdetail/', views.Bkdetail),
    path('Codetail/', views.Codetail),
    path('Userdetail/', views.Userdetail),
    path('Userdetail/profile/', views.profileview),
    path('addReview/', views.addReview),
    path('addReview/Bkdetail/', views.Bkdetail),
    path('addBk/', views.addBk),
    path('addBk/Bkdetail/', views.Bkdetail),
    path('addRating/', views.addRating),
    path('addRating/Bkdetail/', views.Bkdetail),
    path('recommendModel/', views.recommendModel),
    path('filter/', views.filter),
    path('goals/', views.goals),
    path('goals/profile/', views.profileview),
    path('goal_detail/', views.goal_detail),
    path('extend/', views.extend),
    path('extend/Bkdetail/', views.Bkdetail),
    path('goal_history/', views.goal_history)
]
