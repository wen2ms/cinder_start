from oslo_utils import strutils
import exception


def check_string_length(
    value, name, min_length=0, max_length=None, allow_all_spaces=False
):
    try:
        strutils.check_string_length(value, name, min_length, max_length)
    except (ValueError, TypeError) as exc:
        raise exception.InvalidInput(reason=exc)

    if not allow_all_spaces and value.isspace():
        message = "%(name)s cannot be all spaces."
        raise exception.InvalidInput(reason=message)