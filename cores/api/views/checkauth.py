from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def check(request):
    """
    Check if current user is authenticated correctly.
    """
    return Response(f"You are authenticated as {request.user}")
