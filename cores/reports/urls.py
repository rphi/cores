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

from .views.report import assetsummary, mostuseddevices, longreservations
from .views import index

urlpatterns = [
    path('', index.index, name="index"),
    path('assetsummary/', assetsummary.assets, name="assetsummary"),
    path('usage/', mostuseddevices.devices, name="usage"),
    path('longreservations/', longreservations.which, name="longreservations")
]
