import exception
import utils


def test_check_metadata_properties():
    metadata = [
        ({"env": "prod", "owner": "foo"}, True),
        ({}, True),
        (None, True),
        ({"": "value"}, False),
        # empty value
        ({"key": ""}, True),
        ({"a" * 256: "value"}, False),
        ({"key": "v" * 256}, False),
        ("not a dict", False),
        # non-string value
        ({"key": 123}, False),
    ]

    for index, (metadata, should_pass) in enumerate(metadata):
        try:
            utils.check_metadata_properties(metadata)
        except exception.Invalid as error:
            print(f"Test case {index} expected: {should_pass}, got: {error}")


if __name__ == "__main__":
    test_check_metadata_properties()
