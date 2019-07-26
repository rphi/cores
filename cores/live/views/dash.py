from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from live.models import ScanConflict, NicScanConflict, LocationScanConflict, ScanSession, OfflineHostWarning

from inventory.models import Nic, Host, Lab, Rack

# Create your views here.

@permission_required('live.view_scanconflict')
def dashboard(request):
    lastscansession = ScanSession.objects.order_by('-timestamp').first()

    conflicts = ScanConflict.objects.filter(status='new')
    offlines = OfflineHostWarning.objects.filter(status='new')

    niccount = Nic.objects.count()

    return render(request, 'www/live/dashboard.html', {
        'lastscan': lastscansession,
        'conflicts': conflicts,
        'conflictcount': conflicts.count() + offlines.count(),
        'offlines': offlines,
        'niccount': niccount
    })

@permission_required('live.modify_scanconflict')
def autofixip(request, id):
    conflict = get_object_or_404(ScanConflict, pk=id)

    if not hasattr(conflict, 'newip'):
        messages.warning(request, 'We can\'t fix that type of conflict automatically.')
        return redirect('livedash')

    conflict.nic.ip = conflict.newip
    conflict.nic.save()

    conflict.status = 'resolved'
    conflict.save()

    messages.success(request, 'We\'ve updated that for you.')
    return redirect('livedash')

@permission_required('live.modify_scanconflict')
def resolved(request, id):
    conflict = get_object_or_404(ScanConflict, pk=id)
    conflict.status = "resolved"
    conflict.save()

    messages.success(request, 'We\'ve marked that as resolved for you.')
    return redirect('livedash')

@permission_required('live.modify_scanconflict')
def ignore(request, id):
    conflict = get_object_or_404(ScanConflict, pk=id)
    conflict.status = "ignore"
    conflict.save()

    messages.success(request, 'We\'ve ignored that conflict for you.')
    return redirect('livedash')

@permission_required('live.modify_offlinewarning')
def resolvedOffline(request, id):
    warning = get_object_or_404(OfflineHostWarning, pk=id)
    warning.status = "resolved"
    warning.save()

    messages.success(request, 'We\'ve marked that as resolved for you.')
    return redirect('livedash')

@permission_required('live.modify_offlinewarning')
def ignoreOffline(request, id):
    warning = get_object_or_404(OfflineHostWarning, pk=id)
    warning.status = "ignore"
    warning.save()

    messages.success(request, 'We\'ve ignored that warning for you.')
    return redirect('livedash')

@permission_required('live.modify_scanconflict')
def fixlocation(request, id):
    conflict = get_object_or_404(ScanConflict, pk=id)

    if not hasattr(conflict, 'newlab'):
        messages.warning(request, 'We can\'t fix that type of conflict here.')
        return redirect('livedash')

    if request.method == 'POST':
        rack = Rack.objects.filter(lab=request.POST['lab'], number=request.POST['rack'])
        if rack.exists():
            conflict.host.rack = rack[0]
            conflict.host.save()
            conflict.status = 'resolved'
            conflict.save()
            
            messages.success(request, 'We\'ve updated that host\'s location.')
            return redirect('livedash')
        else:
            messages.warning(request, 'That rack does not exist. Please try again.')
    
    labs = Lab.objects.all()
    
    return render(request, 'www/live/fixlocation.html', {
        'oldrack': conflict.host.rack,
        'newlab': conflict.newlab,
        'hostname': conflict.host.hostname,
        'ip': conflict.host.ip,
        'nsc': conflict.nsc if conflict.nsc else None,
        'labs': labs
    })