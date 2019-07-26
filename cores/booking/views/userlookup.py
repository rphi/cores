from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from booking.models import Booking, Reservation
from django.forms import forms, fields
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

class usernameForm(forms.Form):
    username = fields.CharField(max_length=100)

@login_required
def index(request):
    if request.method == "GET":
        return render(request, 'www/booking/userlookup/index.html', {
            'form': usernameForm()
        })
    
    form = usernameForm(request.POST)

    try:
        form.full_clean()
    except ValidationError as e:
        form.add_error(e)
        return render(request, 'www/booking/userlookup/index.html', {
            'form': form
        })
    
    user = User.objects.filter(username=form.cleaned_data.get('username'))

    if not user.exists():
        form.add_error('username', 'Can\'t find a user with that username.')
        return render(request, 'www/booking/userlookup/index.html', {
            'form': form
        })
    
    return redirect('userlookup-detail', user.first().id)

@login_required
def search(request, uid):
    user = get_object_or_404(User, id=uid)

    # get all bookings
    bookings = Booking.objects.filter(owner_id=user)
    upcomingbookings = bookings.filter(start__gte=timezone.now(), end__gte=timezone.now()).order_by('-start')
    currentbookings = bookings.filter(start__lt=timezone.now(), end__gte=timezone.now()).order_by('-end')
    pastbookings = bookings.filter(end__lte=timezone.now()).order_by('-end')

    reservations = Reservation.objects.filter(owner_id=user)
    upcomingres = reservations.filter(Q(start__gte=timezone.now()) & Q(Q(end__isnull=True) | Q(end__gte=timezone.now()))).order_by('-start')
    currentres = reservations.filter(Q(start__lt=timezone.now()) & Q(Q(end__isnull=True) | Q(end__gte=timezone.now()))).order_by('-start')
    pastres = reservations.filter(end__lte=timezone.now()).order_by('-end')

    return render(request, 'www/booking/userlookup/detail.html', {
        'querieduser': user,
        'upcomingbookings': upcomingbookings,
        'currentbookings': currentbookings,
        'pastbookings': pastbookings,
        'upcomingres': upcomingres,
        'currentres': currentres,
        'pastres': pastres
    })
