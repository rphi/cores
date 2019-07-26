from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.dateparse import parse_datetime
import operator
from statistics import mean
from django.contrib.auth.models import User

from inventory.models import Host, Card
from booking.models import Booking, Bookable
from datetime import datetime, timedelta

def devices(request):
    # grab devices ordered by % utilised over the past 90 days descending

    bookings = Booking.objects.filter(end__gte=timezone.now() - timedelta(days=90))

    #bookables = bookings.values_list('bookable', flat=True).distinct()
    bookables = [ b for b in Bookable.objects.all() if not b.check_reserved_simple() ]

    entries = []

    for b in bookables:
        hu = {} # dict to store wip data in
        bb = bookings.filter(bookable=b.id) # get relevant bookings
        
        if not bb.exists():
            # no bookings for this bookable
            continue
        
        hu['hostname'] = b.host.hostname
        hu['hardware'] = b.host.hardware
        if b.host.rack:
            hu['location'] = b.host.rack.lab
        else:
            hu['location'] = None
        hu['group'] = b.host.group
        hu['owner'] = b.host.owner
        hu['bookings'] = bb.count()
        
        users = bb.values_list('owner', flat=True) # work out biggest user
        bookingcount = {}
        for u in users:
            bookingcount[u] = bb.filter(owner=u).count()
        hu['biggestuser'] = User.objects.get(id=max(bookingcount.items(), key=operator.itemgetter(1))[0])

        # TODO: this is a terrible for loop and there really ought to be a better way to do this
        startdate = timezone.now() - timedelta(days=90)
        useddays = 0
        for i in range(90):
            if b.check_free(startdate + timedelta(days=i)):
                useddays += 1
        hu['utilization'] = useddays/90
        entries.append(hu)
    
    # as we've got utilization calculated using some *very* expensive db queries, might as well massage
    # that to give us a per hardware type utilization right?

    hardwares = set([b['hardware'] for b in entries])
    htu = []
    for h in hardwares:
        u = []
        bis = [b for b in entries if b['hardware'] == h]
        for x in bis:
            u.append(x['utilization'])
        htu.append( (h, mean(u)) )
    
    # heck let's grab the lab utilization as well

    labs = set([b['location'] for b in entries])
    lu = []
    for l in labs:
        u = []
        bis = [b for b in entries if b['location'] == l]
        for x in bis:
            u.append(x['utilization'])
        lu.append( (l, mean(u)) )

    # get the aggregate server time booked per user

    users = bookings.values_list('owner', flat=True).distinct()
    uh = []
    for u in users:
        bs = bookings.filter(owner_id=u)
        time = timedelta(0)
        for b in bs:
            time += b.end - b.start
        uo = User.objects.get(id=u)
        uh.append( (uo, time) )
    
    uh.sort(key=operator.itemgetter(1), reverse=True)
    lu.sort(key=operator.itemgetter(1), reverse=True)
    htu.sort(key=operator.itemgetter(1), reverse=True)
    entries.sort(key=operator.itemgetter('utilization'), reverse=True)

    return render(request, 'www/reports/utilizationsummary.html', {
        'hosts': entries,
        'hardwares': htu,
        'labs': lu,
        'userhours': uh
    })
