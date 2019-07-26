from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError
from rest_framework.response import Response

def cores_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.

    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if not response:
        # built in exception handler failed

        if type(exc) is ValidationError:
            return Response(exc.error_dict, status=400)

    return response
