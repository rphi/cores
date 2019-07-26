from django.utils import timezone
from datetime import timedelta
from .models import Notice

def maintenanceJobs():
    threemonths = timezone.now() + timedelta(weeks=12)

    expirednotices = Notice.objects.filter(expires__lt=threemonths)
    expirednotices.delete()
