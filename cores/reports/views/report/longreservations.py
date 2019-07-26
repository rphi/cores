from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q

from booking.models import Reservation
from datetime import timedelta

def which(request):
    # grab any long-running reservations (> 6 months)

    longreservations = Reservation.objects.filter( Q(
        Q( Q(end__gt=timezone.now()) | Q(end__isnull=True) ) &
        Q(start__lte=timezone.now()-timedelta(days=6*30))
        ) )

    lr = []
    for r in longreservations:
        lre = {
            'owner': r.owner,
            'host': r.bookable.host,
            'start': r.start,
            'length': (timezone.now() - r.start).days,
            'others': Reservation.objects.filter(Q(owner=r.owner) & Q(Q(end__isnull=True) | Q(end__gte=timezone.now()))).count()
        }
        lr.append(lre)

    return render(request, 'www/reports/longreservations.html', {
        'lr': lr
    })
