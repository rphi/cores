from django.contrib import admin
from .models import Customer, Loan
from django.utils import timezone

# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    base_model=Customer
    search_fields = ('name', 'contact_name')
    ordering = ['name']
    autocomplete_fields = ['internal_contact']

    list_display = ('name', 'contact_name', 'contact_email', 'internal_contact')
    list_filter = ('internal_contact',)
    
@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    autocomplete_fields = ['host', 'customer', 'user']
    base_model=Loan
    readonly_fields = ['returned']

    list_display = ('host', 'customer', 'start', 'due_return', 'returned', 'returned_date', 'user')
    list_filter = ('customer__name', 'returned')

    def save_model(self, request, obj, form, change):
        self.update_inventory(obj)
        super(LoanAdmin, self).save_model(request, obj, form, change)
    
    def update_inventory(self, obj):
        '''
        Make sure the host being booked out is marked as on-loan and booking is
        suspended if it is going offsite.
        '''
        if obj.returned_date is not None:
            if timezone.now() > obj.returned_date:
                obj.returned = True
                if obj.host.status == 'on_loan':
                    obj.host.status = 'new'
                    obj.host.save()
                    if obj.host.bookable:
                        if obj.host.bookable.status == 'suspended':
                            obj.host.bookable.status = 'active'
                            obj.host.bookable.save()
                return
        obj.returned = False
        obj.host.status = 'on_loan'
        obj.host.save()
        return