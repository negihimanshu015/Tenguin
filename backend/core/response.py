from rest_framework.response import Response


def success(data=None, message="Success", status_code=200):
    return Response(
        {
            "message": message,
            "data": data
        },
        status=status_code
    )

def created(data=None, message="Created"):
    return success(data=data, message=message, status_code=201)

def updated(data=None, message="Updated"):
    return success(data=data, message=message, status_code=200)

def deleted(message="Deleted"):
    return success(data=None, message=message, status_code=200)

def no_content():
    return Response(status=204)
