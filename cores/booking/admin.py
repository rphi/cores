from django.contrib import admin
from .models import Booking, Bookable, Reservation

# Register your models here.

def set_active(modeladmin, request, queryset):
    for b in queryset:
        b.status = 'active'
        b.save()

def set_suspended(modeladmin, request, queryset):
    for b in queryset:
        b.status = 'suspended'
        b.save()

def set_inactive(modeladmin, request, queryset):
    for b in queryset:
        b.status = 'inactive'
        b.save()

class BookingAdmin(admin.ModelAdmin):
    ordering = ['start']
    list_display = ('bookable', 'owner', 'start', 'end', 'comment', 'timestamp')
    list_filter = ('owner', 'timestamp')
    search_fields = ('bookable__host__hostname', 'bookable__host__ip', 'comment')
    list_select_related = ('bookable', 'owner')
    autocomplete_fields = ['bookable', 'owner']

admin.site.register(Booking, BookingAdmin)

class ReservationAdmin(admin.ModelAdmin):
    ordering = ['start']
    list_display = ('bookable', 'owner', 'start', 'end', 'comment', 'timestamp')
    list_filter = ('owner', 'timestamp')
    search_fields = ('bookable__host__hostname', 'bookable__host__ip', 'comment')
    list_select_related = ('bookable', 'owner')
    autocomplete_fields = ['bookable', 'owner']

admin.site.register(Reservation, ReservationAdmin)

def custom_title_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper

class BookingInline(admin.TabularInline):
    model = Booking
    fields = ('owner', 'start', 'end', 'comment', 'timestamp')
    readonly_fields = ('owner', 'start', 'end', 'comment', 'timestamp')

class BookableAdmin(admin.ModelAdmin):
    ordering = ['host']
    list_display = ('host', 'status', 'comment', 'active_bookings_count', 'any_upcoming_reservations')
    actions = [ set_suspended, set_active, set_inactive ]
    search_fields = ('host__hostname', 'comment')
    list_filter = (('status', custom_title_filter('bookable status')), ('host__status', custom_title_filter('host status')), 'host__hardware__host_type', 'host__group' )
    list_select_related = ('host', )
    autocomplete_fields = ['host']
    inlines = [BookingInline]

admin.site.register(Bookable, BookableAdmin)
