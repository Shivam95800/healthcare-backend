from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "errors": {},
        }

        if isinstance(response.data, dict):
            detail = response.data.get("detail", None)
            if detail:
                custom_data["message"] = str(detail)
                custom_data["errors"] = {"detail": [str(detail)]}
            else:
                custom_data["message"] = "Validation failed"
                custom_data["errors"] = response.data
        elif isinstance(response.data, list):
            custom_data["message"] = "Validation failed"
            custom_data["errors"] = {"non_field_errors": response.data}
        else:
            custom_data["message"] = str(response.data)

        response.data = custom_data
        return response

    return Response(
        {
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error occurred.",
            "errors": {"detail": [str(exc)]},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
