import webob.exc
import exception
import utils


class Controller:
    @staticmethod
    def validate_name_and_description(body, check_length=True):
        for attribute in ["name", "description", "display_name", "display_description"]:
            value = body.get(attribute)
            if value is not None:
                if check_length:
                    if isinstance(value, str):
                        value = value.strip()
                    try:
                        utils.check_string_length(body[attribute], attribute, 0, 255)
                    except exception.InvalidInput as error:
                        raise webob.exc.HTTPBadRequest(explanation=error.message)
