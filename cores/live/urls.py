"""cores URL Configuration - live

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
from django.views.generic import TemplateView, RedirectView

from .views.dash import dashboard, autofixip, resolved, ignore, fixlocation, resolvedOffline, ignoreOffline
from .views.lists import unknownhosts, hostlist, hostbylabtable

urlpatterns = [
    path('', RedirectView.as_view(url='list/')),
    path('list/', hostlist, name="livelist"),
    path('list/ajaxtable', hostbylabtable, name="livehosttable"),
    path('unknown/', unknownhosts, name="liveunknown"),
    path('dash/', dashboard, name="livedash"),
    path('autofix/nc/<int:id>', autofixip, name="fixnc"),
    path('resolved/<int:id>', resolved, name="resolved"),
    path('ignore/<int:id>', ignore, name="ignore"),
    path('autofix/lc/<int:id>', fixlocation, name="fixlc"),
    path('resolved/o/<int:id>', resolvedOffline, name="resolved-offline"),
    path('ignore/o/<int:id>', ignoreOffline, name="ignore-offline"),
]
