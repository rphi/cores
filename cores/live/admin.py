from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter, PolymorphicInlineSupportMixin, StackedPolymorphicInline

# Register your models here.

from .models import ScanConflict, ScanSession, LocationScanConflict, NicScanConflict, UnknownScanConflict, VirtualHostsScan, OfflineHostWarning, IgnoredMac

class ScanConflictInline(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """
    class LocationScanConflictInline(StackedPolymorphicInline.Child):
        model = LocationScanConflict

    class NicScanConflictInline(StackedPolymorphicInline.Child):
        model = NicScanConflict

    model = ScanConflict
    child_inlines = (
        LocationScanConflictInline,
        NicScanConflictInline,
    )

@admin.register(ScanSession)
class ScanSessionAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    fields = [
        'agent_identifier', 'raw_data', 'timestamp', 'processed', 'result'
        ]
    #inlines = [ ScanConflictInline ]
    readonly_fields = ['timestamp', 'processed', 'result']
    list_filter = ('timestamp', 'agent_identifier', 'processed')
    list_display = ('timestamp', 'agent_identifier', 'processed')

    def save_model(self, request, obj, form, change):
        newobject = True if obj.pk is None else False
        super().save_model(request, obj, form, change)
        if newobject:
            # creating a new object
            obj.process_ingest()
            self.message_user(request, 'Processing scansession ingest.')
        

class ScanConflictChildAdmin(PolymorphicChildModelAdmin):
    base_model=ScanConflict

@admin.register(LocationScanConflict)
class LocationScanConflictAdmin(ScanConflictChildAdmin):
    base_model=LocationScanConflict

@admin.register(NicScanConflict)
class NicScanConflictAdmin(ScanConflictChildAdmin):
    base_model=NicScanConflict

@admin.register(UnknownScanConflict)
class UnknownScanConflictAdmin(ScanConflictChildAdmin):
    base_model=UnknownScanConflict

@admin.register(ScanConflict)
class ScanConflictParentAdmin(PolymorphicParentModelAdmin):
    base_model=ScanConflict
    child_models=(LocationScanConflict, NicScanConflict, UnknownScanConflict)
    list_filter = (PolymorphicChildModelFilter,)

@admin.register(VirtualHostsScan)
class VirtualHostsScanAdmin(admin.ModelAdmin):
    list_filter = ('lab', 'status', 'lastseen')
    list_display = ('mac', 'ip', 'lab', 'status', 'scan', 'lastseen')

@admin.register(OfflineHostWarning)
class OfflineHostWarningAdmin(admin.ModelAdmin):
    list_filter = ('status', 'timestamp')
    list_display = ('host', 'status', 'host__lab', 'host__lastseen', 'timestamp')

    def host__lab(self, obj):
        return obj.host.rack.lab if obj.host.rack else None
    
    def host__lastseen(self, obj):
        return obj.host.lastseen

@admin.register(IgnoredMac)
class IgnoredMacAdmin(admin.ModelAdmin):
    list_display = ('mac', 'reason', 'created')
