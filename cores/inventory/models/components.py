from django.db import models
from .host import Host
from django.core.exceptions import ValidationError
from django.db.models import Q
from netfields import InetAddressField, MACAddressField, NetManager

class CardType(models.Model):
    name = models.CharField(max_length=30)
    comments = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.name

class Card(models.Model):
    cardtype = models.ForeignKey(CardType, on_delete=models.PROTECT)
    details = models.CharField(max_length=120, blank=True)
    asset_no = models.CharField(max_length=30, blank=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='cards', blank=True, null=True)

    def __str__(self):
        return self.cardtype.name + ' : ' + self.asset_no

class Nic(models.Model):
    model = models.CharField(max_length=30, blank=True)
    mac = MACAddressField(unique=True)
    integrated = models.BooleanField(default=False)
    management = models.BooleanField(default=False)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='nics', null=True, blank=True)
    ip = InetAddressField(store_prefix_length=False, blank=True, null=True)
    primary = models.BooleanField(help_text="Is this the primary NIC in the assigned host?")
    lastseen = models.DateTimeField(null=True, blank=True, help_text="Updated automatically from primary LabScan")
    objects = NetManager()

    def __str__(self):
        return str(self.mac) + ' / ' + self.model

    def clean(self):
        if self.host:
            primaries = Nic.objects.filter(Q(primary=True) & Q(host=self.host) & ~Q(pk=self.pk))
            if primaries.count() > 1:
                raise ValidationError(f"The assigned host cannot have more than one primary NIC, id(s) {primaries.all()}")

    def save(self, *args, **kwargs):
        self.full_clean()

        # update the IP fields on the card's parent host if it has one.
        if self.host!=None and self.ip:
            if self.primary:
                self.host.ip = self.ip
            elif self.host.ip == None:
                primarynic = self.host.nics.filter(primary=True)
                if primarynic:
                    if primarynic[0].ip is None:
                        self.host.ip = self.ip
            if self.host.lastseen:
                if self.lastseen > self.host.lastseen:
                    self.host.lastseen = self.lastseen
            else:
                self.host.lastseen = self.lastseen
            self.host.save()

        return super().save(*args, **kwargs)