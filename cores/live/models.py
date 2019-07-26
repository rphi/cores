from django.db import models, IntegrityError
from polymorphic.models import PolymorphicModel
from inventory.models import Host, Lab, Nic
from polymorphic.showfields import ShowFieldType
from django.utils import timezone, dateparse
from netfields import InetAddressField, MACAddressField
from netaddr.eui import NotRegisteredError
from ipaddress import ip_address, ip_network
from django.db.models import Value, CharField, F, ExpressionWrapper, Q
from netaddr import EUI
from netaddr.core import AddrFormatError
import json

# Create your models here.

class ScanSession(models.Model):
    timestamp = models.DateTimeField(default=timezone.now, null=False)
    agent_identifier = models.CharField(max_length=100)
    raw_data = models.TextField()
    processed = models.BooleanField(default=False, help_text="Has this session's data been successfully processed?")
    result = models.TextField(help_text="Output of ingest process")

    __original_data = None
    __original_agent_identifier = None

    def __init__(self, *args, **kwargs):
        super(ScanSession, self).__init__(*args, **kwargs)
        self.__original_data = self.raw_data
        self.__original_agent_identifier = self.agent_identifier

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.__original_data is not '':
                if (self.__original_data is not self.raw_data) or (self.__original_agent_identifier is not self.agent_identifier):
                    raise IntegrityError("You cannot modify a scansession.")
        super().save(*args, **kwargs)
        
    def get_macs(request):
        return [(n['id'], str(n['mac'])) for n in Nic.objects.all().values('id','mac')]

    def process_ingest(self):
        ss = self

        nets = Lab.objects.all().values('id', 'network')
        imacs = IgnoredMac.objects.all().values_list('mac', flat=True)

        response = []
        seenmacs = []
        seennicids = []
        
        try:
            for r in json.loads(self.raw_data):
                if 'nic' in r:
                    try:
                        n = Nic.objects.get(id=r['nic'])
                    except Nic.DoesNotExist:
                        response.append({
                            "nic": r['nic'],
                            "error": "Does Not Exist"
                        })
                        continue
                elif 'mac' in r:
                    if r['mac'] in seenmacs:
                        response.append({
                            "nic": r['mac'],
                            "error": "already processed this mac, ignoring"
                        })
                        continue

                    try:
                        eui = EUI(r['mac'])
                    except AddrFormatError:
                        response.append({
                            "nic": r['mac'],
                            "error": "not a valid mac address"
                        })
                        continue

                    if eui in imacs:
                        response.append({
                            "nic": r['mac'],
                            "error": "mac in ignoredmacs, skipping"
                        })
                        continue

                    seenmacs.append(r['mac'])

                    try:
                        n = Nic.objects.get(mac=r['mac'])
                    except Nic.DoesNotExist:
                        # check this isn't a virtual mac
                        if (EUI(r['mac']).words[0] & 0b00000010) > 0:
                            vs = VirtualHostsScan.objects.filter(mac=r['mac']).exclude(status='ignore')
                            if vs.exists():
                                # we've already got an entry
                                if not vs.count() > 1:
                                    # update the entry
                                    entry = vs[0]
                                    entry.lastseen = self.timestamp
                                    entry.status = 'active'
                                    
                                    scanip = ip_address(r['ip'])
                                    if not vs[0].ip.ip == scanip:
                                        # its IP has changed
                                        entry.ip = scanip                                
                                    entry.save()
                                    response.append({
                                            "nic": str(r['mac']),
                                            "success": "updated Virtual host entry"
                                        })
                                    continue
                                else:
                                    # why tho this shouldn't happen
                                    # kill them all and start again
                                    vs.delete()
                            
                            # create entry for this host
                            newlab = nets.filter(network__net_contains=ip_address(r['ip']))
                            VirtualHostsScan(
                                scan = ss,
                                ip = r['ip'],
                                mac = r['mac'],
                                lab = Lab.objects.get(id=newlab[0]['id']) if newlab.exists() else None,
                                lastseen = self.timestamp
                            ).save()
                            response.append({
                                "nic": str(r['mac']),
                                "success": "Created new Virtual host entry"
                            })
                            continue

                        # create new unknownscanconflict
                        # check that we don't already have a duplicate conflict
                        dups = UnknownScanConflict.objects.filter(Q(mac=r['mac']) & Q( Q(status='new') | Q(status='ignore') )).order_by('-scan')
                        for d in dups:
                            if not d.ip.ip == ip_address(r['ip']):
                                # mark old conflict as superseded
                                d.status = 'super'
                                d.save()
                            else:
                                # update lastseen on existing conflict
                                d.lastseen = self.timestamp
                                d.save()
                        if not dups.all():
                            newlab = nets.filter(network__net_contains=ip_address(r['ip']))
                            usc = UnknownScanConflict(
                                scan = ss,
                                ip = r['ip'],
                                mac = r['mac'],
                                lab = Lab.objects.get(id=newlab[0]['id']) if newlab.exists() else None,
                                lastseen = self.timestamp
                            )
                            usc.save()
                            response.append({
                                "nic": str(r['mac']),
                                "success": "Created new UnknownScanConflict"
                            })
                        else:
                            response.append({
                                "nic": str(r['mac']),
                                "success": "matching USC already exists"
                            })
                        continue

                # check if we've already processed an entry for this nic this pass
                if n.id in seennicids:
                    response.append({
                        "nic": r['mac'],
                        "error": "already processed this nic, ignoring"
                    })
                    continue
                
                # mark this nic as processed so we can ignore it if we see it again this pass
                seennicids.append(n.id)

                # clear out any old UnknownScanConflicts if they exist
                UnknownScanConflict.objects.filter(Q(mac=n.mac) & Q( Q(status='new') | Q(status='ignore') )).update(status='resolved')

                # check for IP conflict
                ip = ip_address(r['ip'])
                nsc = None

                if not ip == n.ip:
                    if n.ip == None:
                        # if we haven't seen an IP yet for this nic, just accept whatever we find
                        n.ip = ip

                        if hasattr(n, 'host'):
                            # mark 'new' host as active, as we've seen it alive
                            if n.host.status == 'new':
                                n.host.status = 'active'
                        
                        n.save()
                        response.append({
                            "nic": str(r['mac']),
                            "success": "First IP for this NIC."
                        })
                    
                    else:
                        # check that we don't already have a duplicate conflict
                        dups = NicScanConflict.objects.filter(Q(nic=n) & Q( Q(status='new') | Q(status='ignored') )).order_by('-scan')

                        for d in dups:
                            if not d.newip.ip == ip:
                                # mark old conflict as superseded
                                d.status = 'super'
                                d.save()
                        
                        if not dups.all():
                            # we're good to create an entry
                            nsc = NicScanConflict(
                                scan = ss,
                                nic = n,
                                newip = r['ip']
                            )
                            nsc.save()
                            response.append({
                                "nic": str(n.mac),
                                "success": "created nic conflict"
                            })
                        else:
                            response.append({
                                "nic": str(n.mac),
                                "success": "matching nic conflict already exists"
                            })
                    
                    if hasattr(n, 'host'):
                        host = n.host

                        # clear out any offline warnings
                        OfflineHostWarning.objects.filter(host=host.id).update(status='super')

                        # we can confirm the host's location by subnet
                        # NOTE: This will only work on Postgres - SQLite doesn't have the required
                        #       data types to handle the django-netfields queries.
                        
                        if host.rack:
                            net = n.host.rack.lab.network
                            ip = ip_address(r['ip'])
                            if ip not in ip_network(net):
                                # ip doesn't match assigned lab
                                newlab = nets.filter(network__net_contains=ip)

                                # again look for existing conflicts
                                dups = LocationScanConflict.objects.filter(Q(host=host) & Q( Q(status='new') | Q(status='ignore') ))

                                for d in dups:
                                    if d.newlab is not newlab[0]:
                                        # replace this with the new conflict
                                        d.delete()
                                
                                if not dups.all():
                                    LocationScanConflict(
                                        scan=ss,
                                        host=host,
                                        nsc=nsc, # attach IP conflict if there is one
                                        newlab=Lab.objects.get(id=newlab[0]['id']) if newlab.exists() else None # attach newlab suggestion if there is one
                                    ).save()
                                    response.append({
                                        "nic": str(n.mac),
                                        "success": "created locationconflict"
                                    })
                                else:
                                    response.append({
                                        "nic": str(n.mac),
                                        "success": "matching location conflict already exists"
                                    })
                            else:
                                # delete any conflicts as we're up to date
                                LocationScanConflict.objects.filter(Q(host=host) & Q( Q(status='new') | Q(status='ignore') )).update(status='resolved')
                        else:
                            # host doesn't have a rack
                            newlab = nets.filter(network__net_contains=ip)

                            if newlab.exists():
                                # again look for existing conflicts
                                dups = LocationScanConflict.objects.filter(Q(host=host) & Q( Q(status='new') | Q(status='ignore') ))

                                for d in dups:
                                    if d.newlab is not newlab[0]:
                                        # replace this with the new conflict
                                        d.delete()
                                
                                if not dups.all():
                                    newlab = Lab.objects.get(id=newlab[0]['id']) if newlab.exists() else None

                                    if newlab:
                                        zerorack = newlab.racks.filter(number=0)
                                        if zerorack.exists():
                                            # just accept this, and stick the host in the default rack.
                                            host.rack = zerorack[0]
                                            host.save()
                                            response.append({
                                                "nic": str(n.mac),
                                                "success": "accepted 0 rack in lab as initial location"
                                            })
                                        else:
                                            LocationScanConflict(
                                                scan=ss,
                                                host=host,
                                                nsc=nsc, # attach IP conflict if there is one
                                                newlab=newlab # attach newlab suggestion if there is one
                                            ).save()
                                            response.append({
                                                "nic": str(n.mac),
                                                "success": "created initial location conflict with newlab."
                                            })
                                    else:
                                        LocationScanConflict(
                                            scan=ss,
                                            host=host,
                                            nsc=nsc, # attach IP conflict if there is one
                                        ).save()
                                        response.append({
                                            "nic": str(n.mac),
                                            "success": "created initial location conflict without newlab."
                                        })
                                else:
                                    response.append({
                                        "nic": str(n.mac),
                                        "success": "matching location conflict already exists"
                                    })
            
                else:
                    # delete any conflicts as we're up to date
                    NicScanConflict.objects.filter(Q(nic=n) & Q( Q(status='new') | Q(status='ignore') )).update(status='resolved')
                    response.append({
                        "nic": str(n.mac),
                        "success": "Success: DB up to date"
                    })
                
                # update lastseen
                n.lastseen = self.timestamp
                n.save()
        except Exception as e:
            response.insert(0, {"FATAL_ERROR": "Unhandled exception thrown", "e": str(e)})
            ss.result = response
            ss.save()
            return {
                'success': False,
                'result': response
            }
        
        ss.processed = True
        ss.result = response
        ss.save()

        return {
            'success': True,
            'result': response
        }

# workaround for https://github.com/django-polymorphic/django-polymorphic/issues/229#issuecomment-398434412
def NON_POLYMORPHIC_CASCADE(collector, field, sub_objs, using):
        return models.CASCADE(collector, field, sub_objs.non_polymorphic(), using)

class ScanConflict(ShowFieldType, PolymorphicModel):
    scan = models.ForeignKey(ScanSession, on_delete=NON_POLYMORPHIC_CASCADE, related_name='conflicts')
    status = models.CharField(
        max_length=8,
        choices=[
            ('new', 'New'),
            ('resolved', 'Resolved'),
            ('ignore', 'Ignored'),
            ('super', 'Superseded')
        ],
        null=False,
        default='new'
    )

    def __str__(self):
        return f'{self.id} : {self.scan.timestamp}'

class NicScanConflict(ScanConflict):
    newip = InetAddressField(null=True)
    nic = models.ForeignKey(Nic, on_delete=models.CASCADE)

    def __str__(self):
        return f"[nic conflict] {self.nic}: {self.nic.ip} vs {self.newip}"

class LocationScanConflict(ScanConflict):
    newlab = models.ForeignKey(Lab, on_delete=models.PROTECT, blank=True, null=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    nsc = models.ForeignKey(NicScanConflict, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        if self.host.rack is not None:
            return f"[location conflict] {self.host.hostname}: {self.host.rack.lab} vs {self.newlab}"
        else:
            return f"[location conflict] {self.host.hostname}: unknown vs {self.newlab}"

class UnknownScanConflict(ScanConflict):
    ip = InetAddressField()
    mac = MACAddressField()
    lab = models.ForeignKey(Lab, on_delete=models.SET_NULL, null=True, blank=True)
    lastseen = models.DateTimeField(default=timezone.now)

    def safe_OUI_org(self):
        try:
            return self.mac.info['OUI']['org']
        except NotRegisteredError:
            return "unknown"

    def __str__(self):
        return f"[unknown conflict] {self.mac} with IP {self.ip} firstseen at {self.scan.timestamp}"

class VirtualHostsScan(models.Model):
    scan = models.ForeignKey(ScanSession, on_delete=models.CASCADE, related_name='virtualhosts')
    status = models.CharField(
        max_length=8,
        choices=[
            ('active', 'Active'),
            ('old', 'Old'),
            ('ignore', 'Ignored'),
            ('super', 'Superseded')
        ],
        null=False,
        default='active'
    )
    ip = InetAddressField()
    mac = MACAddressField()
    lab = models.ForeignKey(Lab, on_delete=models.SET_NULL, null=True, blank=True)
    lastseen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Virtual MAC: {self.mac}/{self.ip} in {self.lab}"

class OfflineHostWarning(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=8,
        choices=[
            ('new', 'New'),
            ('resolved', 'Resolved'),
            ('ignore', 'Ignored'),
            ('super', 'Superseded')
        ],
        null=False,
        default='new'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.host} lastseen {self.host.lastseen}"

class IgnoredMac(models.Model):
    mac = MACAddressField()
    reason = models.TextField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.mac)