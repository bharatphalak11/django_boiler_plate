from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response:
        return response

    return Response({"detail": str(exc) or "A server error occurred!"}, status=500)