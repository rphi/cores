from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers, serializers, viewsets
from rest_framework.documentation import include_docs_urls
from inventory.models import Nic, Host, HdVendor, HostHardware, HostType, Rack, Building, Lab, Card, CardType

from .viewsets import *
from .views import livescan, ingest, checkauth, cron

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'inventory/hdvendor', HdVendorViewSet)
router.register(r'inventory/hosthardware', HostHardwareViewSet)
router.register(r'inventory/hosttype', HostTypeViewSet)
router.register(r'inventory/lab', LabViewSet)
router.register(r'inventory/rack', RackViewSet)
router.register(r'inventory/building', BuildingViewSet)
router.register(r'inventory/card', CardViewSet)
router.register(r'inventory/cardtype', CardTypeViewSet)

# ID serialized for easy use from import script
router.register(r'inventory/nicbyid', NicIDViewSet)
router.register(r'inventory/hostbyid', HostIDViewSet)
router.register(r'inventory/nic', NicViewSet)
router.register(r'inventory/host', HostViewSet)

# Bookable view
router.register(r'booking/bookable', BookableViewSet)
router.register(r'booking/booking', BookingViewSet)

router.register(r'auth/users', UserViewSet)
router.register(r'auth/groups', GroupViewSet)

urlpatterns = [
    path('live/ingest', livescan.ingest),
    path('live/macs', livescan.macs),
    path('import/gethosttype', ingest.getorcreate_hosttype),
    path('import/gethosthardware', ingest.getorcreate_hosthardware),
    path('auth-test', checkauth.check),
    path('cron/morningjobs', cron.morningjobs),
    path('cron/maintenance', cron.maintenance),
    path('docs', include_docs_urls(title='Cores API Docs')),
    path('', include(router.urls))
]