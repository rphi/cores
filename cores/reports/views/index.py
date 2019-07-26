from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render

def index(request):
    return render(request, 'www/reports/index.html')