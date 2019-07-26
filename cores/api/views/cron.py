from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from booking import cron_jobs as bookingcron
from live import cron_jobs as livecron
from notices import cron_jobs as noticecron

@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def morningjobs(request):
    """
    Trigger cron jobs for morning things
    """
    bookingcron.morningJob()
    return Response("Run morningJobs")

@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def maintenance(request):
    """
    Trigger cron jobs for maintenance things
    """
    bookingcron.maintenanceJob()
    livecron.maintenanceJobs()
    noticecron.maintenanceJobs()
    return Response("Run maintenanceJobs")
