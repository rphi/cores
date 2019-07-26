from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now, make_aware, get_current_timezone
from django.db.models import Q
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.contrib.auth.models import User

from django.contrib.auth.decorators import permission_required, login_required
from booking.models import Bookable, Booking, BookableStatus, Reservation
from inventory.models import Nic, Card
from datetime import datetime, timedelta
from booking import mail

def host(request, id):
    # get bookable
    bookable = get_object_or_404(Bookable, pk=id)

    free = bookable.check_booked_simple() 
    reserved = bookable.check_reserved_simple()
    calendar = bookable.get_calendar()
    
    reservations = bookable.get_reservations()
    if not reserved:
        availability = getcalendarsummary(calendar, reservations)
    else:
        availability = [False] * 14

    nics = Nic.objects.filter(host=bookable.host)
    cards = Card.objects.filter(host=bookable.host)

    return render(request, 'www/booking/host.html', {
        'bookable': bookable,
        'freestate': free,
        'calendar': calendar,
        'reservations': reservations,
        'availability': availability,
        'cards': cards,
        'nics': nics
        })

def getcalendarsummary(calendar, reservations):
    availability = [True] * 14
    nextres = reservations.filter(start__gte=datetime.fromordinal(now().date().toordinal()), start__date__lte=make_aware(datetime.fromordinal((now().date()+timedelta(days=14)).toordinal())))
    if nextres.exists():
        # reservation starting in the next 14 days.
        daystill = (nextres[0].start.date() - now().date()).days
        availability[daystill:] = [False] * (14 - daystill)
    for i in range(14):
        if availability[i] == False:
            continue
        rangestart = make_aware(datetime.fromordinal((now().date()+timedelta(days=i)).toordinal()))
        rangeend = make_aware(datetime.fromordinal((now().date()+timedelta(days=i)+timedelta(hours=23, minutes=59, seconds=59)).toordinal()))
        if calendar.filter(start__lte=rangestart, end__gte=rangeend):
            availability[i] = False
    
    return availability

@login_required(login_url='/account/login')
def book(request, id):
    bookable = get_object_or_404(Bookable, pk=id)

    if request.method == 'POST':
        booking = Booking(
            bookable = bookable,
            owner = request.user,
            start = make_aware(datetime.strptime(request.POST['start'], "%Y-%m-%d")),
            end = make_aware(datetime.strptime(request.POST['end'], "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)), # book to end of day
            comment = request.POST['comment']
        )

        try:
            if bookable.status != 'active':
                raise ValidationError({'__all__': 'Host is not currently bookable.'})
        
            if booking.start.date() < now().date():
                raise ValidationError({'start': 'Booking cannot start in the past.'})
        
            if booking.end.date() < now().date():
                raise ValidationError({'end': 'Booking cannot end in the past.'})
            
            if bookable.check_reserved():
                raise ValidationError({'__all__': "Item is currently reserved."})
            
            if (booking.end - booking.start) > timedelta(days=31):
                raise ValidationError({'end': "Bookings have a maximum duration of one month (31 days). You may want to reserve this machine instead."})

            booking.save()
        except ValidationError as e:
            form = BookingForm(instance=booking)
            form.errors.update(e)
            availability = getcalendarsummary(bookable.get_calendar(), bookable.get_reservations())
            return render(request, 'www/booking/book.html', {
                    'form': form,
                    'availability': availability,
                    'bookable': bookable,
                })
        
        mail.send_booking_confirmation(booking)

        messages.success(request, 'Booking created.')
        return redirect(host, id)

    availability = getcalendarsummary(bookable.get_calendar(), bookable.get_reservations())
    form = BookingForm()

    return render(request, 'www/booking/book.html', {
        'form': form,
        'availability': availability,
        'bookable': bookable,
        })

@login_required(login_url='/account/login')
def reserve(request, id):
    bookable = get_object_or_404(Bookable, pk=id)

    if not request.user.has_perm('booking.add_reservation'):
        messages.error(request, "You do not have permission to add a reservation.")
        return redirect(host, id)


    if request.method == 'POST':

        reservation = Reservation(
            bookable = bookable,
            owner = get_object_or_404(User, pk=request.POST['owner']) if request.POST['owner'] else request.user,
            start = make_aware(datetime.strptime(request.POST['start'], "%Y-%m-%d")),
            comment = request.POST['comment']
        )

        try:
            reservation.save()
        except ValidationError as e:
            form = ReservationForm(instance=reservation)
            form.errors.update(e)
            return render(request, 'www/booking/reserve.html', {
                    'form': form,
                    'bookable': bookable
                })
        
        mail.send_reservation_confirmation(reservation)

        messages.success(request, 'Reservation created.')
        return redirect(host, id)

    form = ReservationForm(initial={'owner': request.user})

    return render(request, 'www/booking/reserve.html', {
        'form': form,
        'bookable': bookable
        })

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('start', 'end', 'comment')

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('start', 'comment', 'owner')

def cancel(request, what, id):
    
    # what is what?
    # to save having two of these being identical, you pass 'b' for booking or 'r' for
    # reservation and it lets us reuse this view function

    if what == 'b':
        target = get_object_or_404(Booking, pk=id)
    elif what == 'r':
        target = get_object_or_404(Reservation, pk=id)
    else:
        return HttpResponseBadRequest("Invalid parameters.")
    
    if (target.start < now() and target.end == None):
        started = True
    else:
        started = False
    
    if request.method == 'POST':
        if started:
            return HttpResponseBadRequest("You can't delete an event that's already happened or currently in progress.")
        target.delete()

        if what is 'b':
            mail.send_booking_cancellation(target)
        elif what is 'r':
            mail.send_reservation_cancellation(target)
        
        messages.success(request, "Successfully deleted booking.")
        return redirect('dash')
    
    return render(request, 'www/booking/cancel.html', {
        'inprogress': started,
        'target': target,
        'what': what
    })
    
    