from booking import mail
from django.db.models import Q
from booking.models.bookable import Bookable, Booking, Reservation
from django.utils.timezone import now, make_aware
from datetime import timedelta, datetime

def morningJob():
    # send out our daily notification emails
    tomorrow = datetime.fromordinal(now().date().toordinal()) + timedelta(1)
    tomorrow_bookings = Booking.objects.filter(start__date=tomorrow)
    tomorrow_reservations = Reservation.objects.filter(start__date=tomorrow)
    ending_bookings = Booking.objects.filter(end__date=tomorrow)
    ended_bookings = Booking.objects.filter(end__date=datetime.fromordinal(now().date().toordinal()))
    
    for b in tomorrow_bookings:
        if not b.mail_start_reminder_sent:
            last_booking = Booking.objects.filter(bookable__id=b.bookable.id).order_by("-end")
            if last_booking.exists():
                mail.send_booking_reminder_last(b, last_booking[0])
            else:
                mail.send_booking_reminder(b)
            b.mail_start_reminder_sent = True
            b.save()
        
    for r in tomorrow_reservations:
        if not r.mail_start_reminder_sent:
            mail.send_reservation_reminder(b)
            r.mail_start_reminder_sent = True
            r.save()
    for b in ending_bookings:
        if not b.mail_end_reminder_sent:
            nextbooking = b.bookable.get_calendar(future=True).first()
            if nextbooking:
                if nextbooking.start <= now() + timedelta(3):
                    mail.send_booking_ending_hard(b, nextbooking)
                else:
                    mail.send_booking_ending(b)
            else:
                mail.send_booking_ending(b)
            b.mail_end_reminder_sent = True
            b.save()
    for b in ended_bookings:
        if not b.mail_end_sent:
            nextbooking = b.bookable.get_calendar(future=True).first()
            if nextbooking:
                if nextbooking.start <= now() + timedelta(3):
                    mail.send_booking_ended_hard(b, nextbooking)
                else:
                    mail.send_booking_ended(b)
            else:
                mail.send_booking_ended(b)
            b.mail_end_sent = True
            b.save()
    
    threemonths = now() - timedelta(weeks=12)
    neednagging = Reservation.objects.filter(mail_last_nag__lt=threemonths)
    for r in neednagging:
        mail.send_reservation_nag(r)
        r.mail_last_nag = now()
        r.save()

def maintenanceJob():
    threemonths = now() - timedelta(weeks=12)

    oldbookings = Booking.objects.filter(end__lt=threemonths)
    oldbookings.delete()

    oldreservations = Reservation.objects.filter(end__lt=threemonths, end__isnull=False)
    oldreservations.delete()
