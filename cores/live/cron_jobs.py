from live.models import ScanConflict, ScanSession, UnknownScanConflict, NicScanConflict, LocationScanConflict, VirtualHostsScan, OfflineHostWarning
from inventory.models import Nic, Host
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

def maintenanceJobs():
    # remove any conflicts that have been fixed and not marked as such
    lscs = LocationScanConflict.objects.filter(status='new')
    for lsc in lscs:
        if lsc.host.rack:
            if lsc.host.rack.lab == lsc.newlab:
                lsc.status = 'resolved'
                lsc.save()
                continue
            elif lsc.host.ip in lsc.host.rack.lab.network:
                lsc.status = 'resolved'
                lsc.save()
                continue
    
    nscs = NicScanConflict.objects.filter(status='new')
    for nsc in nscs:
        if nsc.nic.ip == nsc.newip:
            nsc.status = 'resolved'
            nsc.save()
            continue
    
    uscs = UnknownScanConflict.objects.filter(status='new')
    for usc in uscs:
        if Nic.objects.filter(mac=usc.mac).exists():
            usc.status = 'resolved'
            usc.save()
            continue
    
    # clear old scansessions
    threemonths = timezone.now() - timedelta(weeks=12) 
    oldsessions = ScanSession.objects.filter(timestamp__lt=threemonths)
    for s in oldsessions:
        activeconflicts = s.conflicts.filter(status='active').count()
        if activeconflicts > 0:
            # can't delete entire session, just delete old conflicts
            staleconflicts = s.conflicts.exclude(status='active')
            staleconflicts.delete()
        else:
            s.delete()
    
    # cleanup offline warnings
    OfflineHostWarning.objects.filter(timestamp__lt=threemonths).exclude(status='active').delete()

    # create offline warnings
    twodays = timezone.now() - timedelta(hours=48)
    stalehosts = Host.objects.filter(status='active', lastseen__lt=twodays)
    for h in stalehosts:
        oldwarnings = OfflineHostWarning.objects.filter(host=h.id, status__in=['new', 'ignore'])
        if not oldwarnings.exists():
            OfflineHostWarning(host = h).save()

    # cleanup old vhosts
    VirtualHostsScan.objects.filter(lastseen__lt=threemonths).exclude(status='active').delete()

    # hide stale virtual hosts
    VirtualHostsScan.objects.filter(lastseen__lt=twodays).exclude(status='ignore').update(status='old')
    