from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled, NotFound, ValidationError, PermissionDenied


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):  # check that a Throttled exception is raised
        custom_response_data = {  # prepare custom response data
            'msg': 'request limit exceeded',
            'availableIn': '%d minutes.' % int(exc.wait/60)
        }
        # set the custom response data on response object
        response.data = custom_response_data

    if isinstance(exc, PermissionDenied):

        if exc.detail.code == 'user_not_verified':
            custom_response_data = {  # prepare custom response data
                'msg': exc.detail
            }

            response.data = custom_response_data

    return response


def get_object_or_404_custom(model, *args, **kwargs):
    msg = kwargs.pop('msg', 'Object not found')
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        raise NotFound({"msg": msg})


def raise_400_HTTP_if_serializer_invalid(serializer):


    if not serializer.is_valid():
        
        
        for field, errors in serializer.errors.items():
            if field:
                field_label = serializer.fields[field].label
                for error in errors:
                    raise ValidationError({"msg": f"Invalid field '{field_label}': {error}"})
            else:
                raise ValidationError({"msg": error})



        raise ValidationError({"msg": "Unexpected error."})

