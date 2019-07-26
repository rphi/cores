from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.exceptions import APIException
import json

from inventory.models import HostType, HostHardware

@api_view(['POST'])
@permission_classes((permissions.IsAdminUser,))
def getorcreate_hosttype(request):
    """
    Get or create hosttype
    """

    if not all(key in request.data for key in ['name', 'details']):
        raise APIException(
            detail = "Missing parameters",
            code = 400
        )

    hosttype = HostType.objects.get_or_create(
        name = request.data['name'],
        defaults = {
            'details': request.data['details']
        }
    )

    return Response({
        'name': hosttype[0].name,
        'details': hosttype[0].details,
        'id': hosttype[0].id,
        'created': hosttype[1]
    })

@api_view(['POST'])
@permission_classes((permissions.IsAdminUser,))
def getorcreate_hosthardware(request):
    """
    Get or create hosthardware
    """

    if not all(key in request.data for key in ['name', 'host_type', 'details']):
        raise APIException(
            detail = "Missing parameters",
            code = 400
        )
    
    hosttype = HostType.objects.filter(id=request.data['host_type'])

    if not hosttype.exists():
        raise APIException(
            detail = "Invalid hosttype id.",
            code = 400
        )


    hosthardware = HostHardware.objects.get_or_create(
        name = request.data['name'],
        host_type = hosttype[0],
        defaults = {
            'details': request.data['details']
        },
    )

    return Response({
        'name': hosthardware[0].name,
        'details': hosthardware[0].details,
        'host_type': hosthardware[0].host_type.id,
        'id': hosthardware[0].id,
        'created': hosthardware[1]
    })