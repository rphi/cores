from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render

from booking.models import Bookable, Booking, Reservation, BookableStatus
from inventory.models import Building, CardType, HostType, HostHardware, Host
from notices.models import Notice
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

def dashboard(request):
    if not request.user.is_authenticated:
        return render(request, 'www/booking/notloggedin.html')

    notices = Notice.objects.filter(
        Q(visible=True) &
        Q(Q(expires__gte=timezone.now()) | Q(expires__isnull=True)) &
        Q(Q(target__in=request.user.groups.all()) | Q(target__isnull=True))
    ).order_by('priority', '-timestamp')

    threedaysago = timezone.now() - timedelta(days=3)

    bookings = Booking.objects.filter(owner_id=request.user)
    upcomingbookings = bookings.filter(start__gte=timezone.now(), end__gte=timezone.now()).order_by('-start')
    currentbookings = bookings.filter(start__lt=timezone.now(), end__gte=timezone.now()).order_by('-end')
    pastbookings = bookings.filter(end__lte=timezone.now(), end__gte=threedaysago).order_by('-end')

    reservations = Reservation.objects.filter(owner_id=request.user)
    upcomingres = reservations.filter(Q(start__gte=timezone.now()) & Q(Q(end__isnull=True) | Q(end__gte=timezone.now()))).order_by('-start')
    currentres = reservations.filter(Q(start__lt=timezone.now()) & Q(Q(end__isnull=True) | Q(end__gte=timezone.now()))).order_by('-start')
    pastres = reservations.filter(end__lte=timezone.now(), end__gte=threedaysago).order_by('-end')

    if not request.user.email:
        messages.warning(request, 
        mark_safe('''<h3>Your profile is incomplete</h3>
        <p>We've been unable to pull your profile in from LDAP. Please complete your profile to ensure that you recieve email notifications.</p>
        <a class="btn btn-primary btn-lg" href="/booking/profile">Fix now</a>'''))

    return render(request, 'www/booking/dashboard.html', {
        'upcomingbookings': upcomingbookings,
        'currentbookings': currentbookings,
        'pastbookings': pastbookings,
        'upcomingres': upcomingres,
        'currentres': currentres,
        'pastres': pastres,
        'notices': notices
        })
