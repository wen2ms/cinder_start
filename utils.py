from oslo_utils import strutils
import exception


def check_string_length(value, name, min_length=0, max_length=None, allow_all_spaces=False):
    try:
        strutils.check_string_length(value, name, min_length, max_length)
    except (ValueError, TypeError) as exc:
        raise exception.InvalidInput(reason=exc)

    if not allow_all_spaces and value.isspace():
        message = "%(name)s cannot be all spaces."
        raise exception.InvalidInput(reason=message)


def check_metadata_properties(metadata):
    if not metadata:
        metadata = {}
    if not isinstance(metadata, dict):
        message = "Metadata should be a dict."
        raise exception.InvalidInput(message)

    for k, v in metadata.items():
        try:
            check_string_length(k, "Metadata key: %s" % k, min_length=1)
            check_string_length(v, "Value for metadata key: %s" % k)
        except exception.InvalidInput as exc:
            raise exception.InvalidInputMetadata(reason=exc)

        if len(k) > 255:
            message = "Metadata property key %s greater than 255 characters." % k
            raise exception.InvalidInputMetadataSize(reason=message)
        if len(v) > 255:
            message = "Metadata property key %s value greater than 255 characters." % k
            raise exception.InvalidInputMetadataSize(reason=message)
