from django.db import models
from .location import Rack
from django.utils.timezone import now
from enum import Enum
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from netfields import InetAddressField

class HostType(models.Model):
    name = models.CharField(max_length=30)
    details = models.CharField(max_length=120, blank=True)
    
    def __str__(self):
        return self.name

class HostHardware(models.Model):
    name = models.CharField(max_length=30)
    details = models.CharField(max_length=120, blank=True)
    host_type = models.ForeignKey(HostType, on_delete=models.PROTECT, null=True, related_name='hardwares')
    
    def __str__(self):
        return f"[{self.host_type}] {self.name}"

class HdVendor(models.Model):
    vendor = models.CharField(max_length=30)

    def __str__(self):
        return self.vendor

class HostStatus(Enum):
    active = "Active"
    missing = "Missing"
    retired = "Retired"
    on_loan = "On Loan"
    unknown = "Unknown"
    offline = "Offline"
    new = "New"

class Host(models.Model):
    hostname = models.CharField(max_length=50, unique=True)
    ip = InetAddressField(help_text="Updated automatically from primary Nic", null=True, blank=True)
    serial_no = models.CharField(max_length=30, null=True, blank=True)
    asset_no = models.CharField(max_length=30, null=True, blank=True)
    diskvendor = models.ForeignKey(HdVendor, on_delete=models.PROTECT, null=True, blank=True)
    hardware = models.ForeignKey(HostHardware, on_delete=models.PROTECT)
    rack = models.ForeignKey(Rack, on_delete=models.PROTECT, null=True, blank=True)
    hypervisor = models.BooleanField(help_text="Does this machine contain VMs?", default=False)
    vm_host = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, help_text="Parent host if this host is virtualized")
    details = models.CharField(max_length=120, blank=True)
    lastseen = models.DateTimeField(null=True, blank=True, help_text="Updated automatically from primary Nic/LabScan")
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='hosts', help_text="User who owns/has been assigned to manage this machine", null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=[(tag.name, tag.value)
                 for tag in HostStatus],  # Choices is a list of Tuple
        null=False,
        default='new',
        help_text="Changing this from Active will automatically suspend this host's bookable if there is an active one."
    )
    group = models.ForeignKey(Group, on_delete=models.PROTECT, help_text='Limit bookings of this host to a specific group', blank=True, null=True)

    def __str__(self):
        return self.hostname
    
    def getprimarynic(self):
        return self.nics.get(primary=True)
    
    def bookable_status(self):
        return self.bookable.status if hasattr(self, 'bookable') else 'none'
    
    def save(self, *args, **kwargs):
        self.full_clean()
        # update bookable for this host if we're taking the host out of service, so
        # people can't book a host that is missing/on loan
        if hasattr(self, 'bookable') and self.status != 'active':
            if self.bookable.status == 'active':
                self.bookable.status = 'suspended'
                self.bookable.save()
        return super().save(*args, **kwargs)
