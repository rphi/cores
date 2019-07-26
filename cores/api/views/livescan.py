from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from live import scanhandler

@api_view(['POST'])
@permission_classes((permissions.IsAdminUser,))
def ingest(request):
    """
    Handle inbound scan data
    """
    result = scanhandler.ingest(request.data)
    return Response(result)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def macs(request):
    """
    Get all macs mapped to Nic ID for livescan
    """
    result = scanhandler.get_macs(request.data)
    return Response(result)