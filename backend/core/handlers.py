from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from core.exceptions import AppExceptions

def drf_exception_handler(exc, context):                
        if isinstance(exc, AppExceptions):
                return Response(
                        {"message" : exc.message},
                        status=exc.status_code
                )
        
        response = exception_handler(exc, context)
        if response is not None:
                return Response(
                        {"message" : response.data.get("detail", "An error occurred.")},
                        status=response.status_code
                )

        return Response(
                {"message":"Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
                
