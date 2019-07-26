from django.shortcuts import render
from django.db.models import Q

from live.models import UnknownScanConflict, VirtualHostsScan
from django.utils import timezone
from collections import OrderedDict
from ipaddress import ip_address
from inventory.models import Host

def unknownhosts(request):
    uscs = UnknownScanConflict.objects.filter(Q(status='new') | Q(status='ignore')).order_by('lab', 'ip')

    return render(request, 'www/live/unknownhosts.html', {
        'uscs': uscs
    })

def hostlist(request):
    return render(request, 'www/live/list.html')

def hostbylabtable(request):
    hosts = Host.objects.all().order_by('rack__lab', 'ip')
    hs = Host.objects.all()

    labhosts = {}
    
    for h in hs:
        lab = str(h.rack.lab) if h.rack else 'None'
        if lab not in labhosts:
            labhosts[lab] = []
        labhosts[lab].append({
            'hostname': h.hostname,
            'ip': h.ip,
            'hardware': h.hardware,
            'lastseen': h.lastseen,
            'status': h.status,
            'bookable': h.bookable.status if hasattr(h, 'bookable') else False,
            'lab': lab
        })
    

    unknownhosts = UnknownScanConflict.objects.filter(status__in=['new', 'ignored'])
    for u in unknownhosts:
        lab = str(u.lab) if hasattr(u, 'lab') else 'None'
        if lab not in labhosts:
            labhosts[lab] = []
        labhosts[lab].append({
            'hostname': '-',
            'ip': u.ip,
            'hardware': '-',
            'lastseen': u.lastseen,
            'status': 'unknown mac',
            'bookable': False,
            'lab': lab
        })


    virtualhosts = VirtualHostsScan.objects.filter(status='active')
    for v in virtualhosts:
        lab = str(v.lab) if hasattr(v, 'lab') else 'None'
        if lab not in labhosts:
            labhosts[lab] = []
        labhosts[lab].append({
            'hostname': '-',
            'ip': v.ip,
            'hardware': 'virtual machine',
            'lastseen': v.lastseen,
            'status': 'unknown vm',
            'bookable': False,
            'lab': lab
        })

    for l in labhosts.keys():
        labhosts[l].sort(key=sortlabs)
    
    labhosts =  OrderedDict(sorted(labhosts.items(), key=lambda t: t[0]))

    return render(request, 'www/live/hostbylabtable.html', {
        'hosts': hosts,
        'labhosts': labhosts
    })

def sortlabs(e):
    if e['ip'] is not None:
        return (e['ip'], e['hostname'])
    else:
        return (ip_address('255.255.255.255'), e['hostname'])

