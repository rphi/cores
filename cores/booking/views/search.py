from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render

from booking.models import Bookable
from inventory.models import Building, CardType, HostType, HostHardware, Host
from django.contrib import messages
from django.utils.safestring import mark_safe

def landing(request):
    buildings = Building.objects.all()
    cards = CardType.objects.all()
    host_types = HostType.objects.all()

    return render(request, 'www/booking/search.html', {
        'buildings': buildings,
        'cards': cards,
        'host_types': host_types
        })
