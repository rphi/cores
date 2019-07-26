from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.dateparse import parse_datetime

from inventory.models import Host, Card
from datetime import datetime, timedelta

def assets(request):
    # poc view to grab all assets and list all their asset numbers
    # at the moment, only host and card have asset numbers.

    hosts = Host.objects.all()
    cards = Card.objects.all()

    return render(request, 'www/reports/assetsummary.html', {
        'hosts': hosts,
        'cards': cards
    })
