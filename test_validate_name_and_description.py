from controller import Controller
import webob.exc

volume = {
    # "name": "  test-volume  " * 300,
    "name": "       ",
    # "name": "  test-volume  ",
    "description": "   this is a test volume description   ",
}

try:
    Controller.validate_name_and_description(volume, check_length=True)
    print("Successfully")
except webob.exc.HTTPBadRequest as error:
    print("Failed:", error)
