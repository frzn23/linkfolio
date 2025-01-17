from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('display/<str:username>', views.display, name='display'),
    path('click/<str:username>/<str:link_type>', views.track_click, name='track_click'),
    path('analytics', views.analytics, name='analytics'),
]
