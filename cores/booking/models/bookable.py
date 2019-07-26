from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from enum import Enum
from inventory.models import Host
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from booking import mail

# generalisable model for bookables, in our case servers

class BookableStatus(Enum):
    created = "Created"
    active = "Active"
    suspended = "Suspended"
    inactive = "Inactive"

class Bookable(models.Model):
    # class used to store booking related information about a host

    status = models.CharField(
        max_length=30,
        choices=[(tag.name, tag.value)
                 for tag in BookableStatus],  # Choices is a list of Tuple
        null=False,
        default=BookableStatus.created
    )

    host = models.OneToOneField(Host, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300, blank=True)

    def save(self, *args, **kwargs):
        if self.status != 'active':
            for b in self.get_calendar():
                mail.send_inactive_bookable(b)
            for r in self.get_reservations():
                mail.send_inactive_bookable(r)

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.host.hostname + '[B]'

    def check_free(self, when=now()):
        bookings = Booking.objects.filter(
            Q(bookable=self) & 
            Q(Q(start__lte=when) & Q(end__gt=when))
        )
        if not bookings:
            return False
        return bookings.first()
    
    def check_booked_simple(self, when=now()):
        booking = self.check_free()
        if booking:
            return f"Booked until {booking.end.strftime('%d/%m/%y')} by {booking.owner}"
        else:
            return False
    
    def get_calendar(self, future=False):
        bookings = Booking.objects.filter(bookable=self).order_by('-start')
        if future:
            bookings = bookings.filter(start__gte=make_aware(datetime.fromordinal(now().date().toordinal())))
        return bookings

    def active_bookings_count(self):
        return Booking.objects.filter(bookable=self).order_by('-start').filter(end__gte=make_aware(datetime.fromordinal(now().date().toordinal()))).count()

    def get_reservations(self, future=False):
        reservations = Reservation.objects.filter(bookable=self)
        if future:
            reservations = reservations.filter(Q(start__gte=make_aware(datetime.fromordinal(now().date().toordinal()))) | Q(end__isnull=True))
        return reservations
    
    def any_upcoming_reservations(self):
        return self.get_reservations(True).exists()
    
    def check_reserved(self, ignore=None):
        reservations=self.reservations.filter(Q(start__lte=now())&Q(Q(end__gte=now()) | Q(end=None)))
        if ignore:
            reservations = reservations.exclude(pk=ignore.pk)
        return reservations.count() > 0
    
    def check_reserved_simple(self, when=now()):
        res = self.check_reserved()
        if res:
            return True
        else:
            return False
    
    def get_current_reservation(self):
        return self.reservations.filter(Q(start__lte=now())&Q(Q(end__gte=now()) | Q(end=None))).first()
        
class Booking(models.Model):
    bookable = models.ForeignKey(Bookable, on_delete=models.CASCADE, related_name='bookings')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bookings')
    start = models.DateTimeField()
    end = models.DateTimeField()
    comment = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)
    mail_start_reminder_sent = models.BooleanField(blank=True, default=False)
    mail_end_reminder_sent = models.BooleanField(blank=True, default=False)
    mail_end_sent = models.BooleanField(blank=True, default=False)
    import_id = models.IntegerField(blank=True, null=True, help_text='ID from import source') # used by import script, old system booking ID

    def clean(self):
        if self.end < self.start:
            raise ValidationError("Booking cannot end before it has started.")

        if self.bookable.host.group:
            if not self.owner.groups.filter(pk=self.bookable.host.group.pk).exists():
                raise ValidationError(f"This host belongs to the {self.bookable.host.group} group, which you are not a member of.")
        
        overlaps = self.bookable.bookings.filter(
                Q(Q(start__gte=self.start) & Q(start__lt=self.end)) | 
                Q(Q(end__gt=self.start) & Q(end__lt=self.end)) |
                Q( Q(start__gte=self.start) & Q(end__lt=self.end)) |
                Q( Q(start__lte=self.start) & Q(end__gte=self.end))
            ).exclude(pk=self.pk)

        if overlaps.count() > 0:
            raise ValidationError("Booking overlaps with another booking.")

        resoverlaps = self.bookable.reservations.filter(
            start__lte=self.end, start__gte=self.start
        )

        if resoverlaps.count() > 0:
            raise ValidationError("Booking overlaps with a future reservation.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.bookable.host.hostname + ' @ ' + self.start.strftime('%Y-%m-%d %H:%M')

class Reservation(models.Model):
    bookable = models.ForeignKey(Bookable, on_delete=models.CASCADE, related_name='reservations')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservations')
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    comment = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)
    mail_start_reminder_sent = models.BooleanField(blank=True, default=False)
    mail_end_sent = models.BooleanField(blank=True, default=False)
    mail_last_nag = models.DateTimeField(default=now, blank=True)

    def clean(self):
        if not ['active'].__contains__(self.bookable.status):
            raise ValidationError('Host is not currently bookable.')
        
        if self.bookable.check_reserved(ignore=self) :
            raise ValidationError('This host is already reserved.')
        
        if self.bookable.host.group:
            if not self.owner.groups.filter(pk=self.bookable.host.group.pk).exists():
                raise ValidationError(f"This host belongs to the {self.bookable.host.group} group, which you are not a member of.")
        
        if self.bookable.reservations.filter(end__isnull=True, start__lte=self.start).exclude(pk=self.pk):
            raise ValidationError('Another reservation is due to start before then.')
        
        if self.end:
            if self.end < self.start:
                raise ValidationError({'end': "Reservation cannot end before it has started."})
            
            overlaps = self.bookable.bookings.filter(
                    Q(start__range=(self.start,self.end)) | 
                    Q(end__range=(self.start,self.end)) |
                    Q( Q(start__gte=self.start) & Q(end__lte=self.end))
                )

            if overlaps.count() > 0:
                raise ValidationError("Reservation overlaps with an existing booking.")
        else:
            if self.bookable.bookings.filter(end__gte=self.start).count() > 0:
                raise ValidationError("Reservation overlaps with existing bookings. Try booking this item instead.")
            if self.bookable.reservations.filter(Q(start__gte=self.start) | Q(end__gte=self.start)).exclude(id=self.id).count() > 0:
                raise ValidationError("Cannot reserve with future reservations. Try booking this item instead.")

    def save(self, *args, **kwargs):
        self.full_clean()
        self.mail_last_nag = self.start
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.bookable.host.hostname + ' reserved from ' + self.start.strftime('%Y-%m-%d %H:%M')
