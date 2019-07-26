"""cores URL Configuration - booking

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import TemplateView

from .views import search, host, dashboard, profile, userlookup

urlpatterns = [
    path('', dashboard.dashboard, name="dash"),
    path('search/', search.landing, name="search"),
    path('host/<int:id>', host.host, name="host"),
    path('host/<int:id>/book', host.book, name="book"),
    path('host/<int:id>/reserve', host.reserve, name="reserve"),
    path('cancel/<what>/<int:id>', host.cancel, name="cancel"),
    path('profile', profile.update_profile, name="profile"),
    path('user', userlookup.index, name="userlookup-index"),
    path('user/<int:uid>/detail', userlookup.search, name="userlookup-detail")
]
