from django.contrib import admin
from .models import Host, Nic, Card, Lab, Building, Rack, HostHardware, HostType, HdVendor, CardType
from booking.models import Bookable
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages

# Register your models here.

def make_bookable(modeladmin, request, queryset):
    for h in queryset:
        Bookable.objects.get_or_create(host=h)

def suspend_bookable(modeladmin, request, queryset):
    for h in queryset:
        b = Bookable.objects.filter(host=h)
        if b.exists():
            i = b.first()
            i.status = 'suspended'
            i.save()

def make_bookable_inactive(modeladmin, request, queryset):
    for h in queryset:
        b = Bookable.objects.filter(host=h)
        if b.exists():
            i = b.first()
            i.status = 'inactive'
            i.save()

def set_online(modeladmin, request, queryset):
    queryset.update(status='online')

def set_offline(modeladmin, request, queryset):
    for h in queryset: # running in for loop as opposed to bulk_update to ensure bookables are suspended
        h.status = 'offline' # when host marked offline - save() isn't called with bulk_update
        h.save()

def set_unknown(modeladmin, request, queryset):
    for h in queryset:
        h.status = 'unknown'
        h.save()

def set_retired(modeladmin, request, queryset):
    for h in queryset:
        h.status = 'retired'
        h.save()

def set_new(modeladmin, request, queryset):
    queryset.update(status='new')

class CardTypeAdmin(admin.ModelAdmin):
    fields = ['name', 'comments']
    search_fields = ['name']
    ordering = ['name']
admin.site.register(CardType, CardTypeAdmin)

class HdVendorAdmin(admin.ModelAdmin):
    fields = ['vendor']
    search_fields = ['vendor']
    ordering = ['vendor']
admin.site.register(HdVendor, HdVendorAdmin)

class NicInline(admin.TabularInline):
    model = Nic
    readonly_fields = ['lastseen']

class CardInline(admin.TabularInline):
    model = Card
    autocomplete_fields = ['cardtype']

class HostAdmin(admin.ModelAdmin):
    fields = [
        'hostname', 'ip', 'hardware', 'status', 'lastseen', 'serial_no', 
        'asset_no', 'diskvendor', 'rack', 'hypervisor', 'vm_host', 'details', 'owner',
        'group'
        ]
    ordering = ['hostname']
    inlines = [ NicInline, CardInline ]
    readonly_fields = ['ip', 'lastseen']
    list_display = ('hostname', 'asset_no', 'hardware', 'details', 'ip', 'lastseen', 'status', 'bookable_status', 'group')
    list_filter = ('status', 'hardware__host_type', 'hardware', 'group', 'rack__lab')
    list_select_related = ('hardware', 'diskvendor', 'group', 'rack', 'vm_host', 'owner')
    search_fields = ('hostname', 'ip', 'asset_no', 'serial_no', 'details', 'nics__mac')
    actions = [make_bookable, suspend_bookable, make_bookable_inactive, set_online, set_unknown, set_offline]
    autocomplete_fields = ['hardware', 'rack', 'vm_host', 'owner', 'group', 'diskvendor']

    def save_model(self, request, obj, form, change):
        # give the admin a heads up that they're taking offline a machine with bookings.
        # it's here and not in the model, as it's not a validationerror, just a warning.
        if (not obj.status == 'active') and hasattr(obj, 'bookable'):
            if obj.bookable.bookings.filter(end__gt=timezone.now()).exists() or obj.bookable.reservations.filter(Q(Q(end__isnull=True) | Q(end__gte=timezone.now()))).exists():
                messages.warning(request, "Heads up! That host is now not active, but has future bookings or reservations. We've suspended the bookable for you if it was active.")
        super(HostAdmin, self).save_model(request, obj, form, change)

admin.site.register(Host, HostAdmin)

class CardAdmin(admin.ModelAdmin):
    list_display = ('asset_no', 'cardtype', 'details', 'host')
    list_filter = ('cardtype', 'host__status')
    autocomplete_fields = ['host']
    search_fields = ['asset_no', 'cardtype', 'details']

admin.site.register(Card, CardAdmin)

class RackInline(admin.TabularInline):
    model = Rack

class LabAdmin(admin.ModelAdmin):
    inlines = [ RackInline ]
    list_display = ('name', 'building', 'network')
    list_filter = ('building',)
    ordering = ['building', 'name']
    search_fields = ['name', 'building', 'network']
admin.site.register(Lab, LabAdmin)

class RackAdmin(admin.ModelAdmin):
    list_display = ('number', 'lab', 'comment')
    list_filter = ('lab', 'lab__building')
    autocomplete_fields = ['lab']
    ordering = ['lab', 'number']
    search_fields = ['number', 'lab', 'lab__building']
admin.site.register(Rack, RackAdmin)

class NicAdmin(admin.ModelAdmin):
    list_display = ('mac', 'ip', 'model', 'host', 'lastseen')
    list_filter = ('model', 'lastseen')
    search_fields = ('mac__icontains', 'host__hostname', 'model')
    autocomplete_fields = ['host']
    ordering = ['mac']
admin.site.register(Nic, NicAdmin)

class HardwareInline(admin.TabularInline):
    model = HostHardware
    fields = ('name', 'details')
class TypeAdmin(admin.ModelAdmin):
    inlines = [ HardwareInline ]
admin.site.register(HostType, TypeAdmin)

class HardwareAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'details', 'host_type')
    list_filter = ('host_type', )
    ordering = ['name']
    search_fields = ['name', 'host_type__name']
admin.site.register(HostHardware, HardwareAdmin)

class LabInline(admin.TabularInline):
    model = Lab

class BuildingAdmin(admin.ModelAdmin):
    inlines = [ LabInline ]
    list_display = ('code', 'comment')
    ordering = ['code']
admin.site.register(Building, BuildingAdmin)
