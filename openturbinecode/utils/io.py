"""This module contains functions to handle input/output operations.
"""

import os
import jsonschema as json
import yaml

from pathlib import Path


def arg_to_path(args, key):
    """Return the path from the args object.

    Args:
        args (dict): Dictionary of arguments.
        key (str): String key to search in the dictionary.

    Returns:
        Path: Path to the file.
    """
    path = getattr(args, key) if key in args else ""
    if path and path[0] != "." and path[0] != os.sep:
        path = "." + os.sep + path
    return path


def load_yaml(fname_input):
    """Loads a yaml file into a python object.

    Args:
        fname_input (Path): Path to the yaml file.

    Returns:
        dict: Dictionary of the yaml object.
    """
    if not fname_input:
        return {}
    with open(fname_input, "r", encoding="utf-8") as f:
        data = f.read()
        input_yaml = yaml.load(data, Loader=yaml.FullLoader)
    return input_yaml


def write_yaml(instance: dict, foutput: Path):
    """Dump a yaml file from a python object.

    Args:
        instance (dict): Dictionary to be dumped.
        foutput (Path): File path to dump the dictionary.
    """

    with open(foutput, "w", encoding="utf-8") as f:
        yaml.dump(instance, f)


def extend_with_default(validator_class: json.Draft7Validator):
    """Validate a json schema with default values.

    Args:
        validator_class (json.Draft7Validator): Validator class.

    Returns:
        json: Validator class with default values.

    Yields:
        _type_: _description_

    See: https://python-jsonschema.readthedocs.io/en/stable/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance  # noqa: E501
    """
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return json.validators.extend(validator_class, {"properties": set_defaults})


DefaultValidatingDraft7Validator = extend_with_default(json.Draft7Validator)


def validate_without_defaults(finput, fschema):
    yaml_schema = load_yaml(fschema) if type(fschema) is type("") else fschema
    myobj = load_yaml(finput) if type(finput) is type("") else finput
    json.Draft7Validator(yaml_schema).validate(myobj)
    return myobj


def validate_with_defaults(finput, fschema):
    """Takes the modeling yaml file input as an argument and outputs it as a
    dictionary named OTCD.modeling_options. Only is called if a modeling yaml file is input.

    Args:
        finput (Path): Path to the input file.
        fschema (_type_): Schema to validate the input file.

    Returns:
        dict: Dictionary of the validated input file.
    """
    yaml_schema = load_yaml(fschema) if type(fschema) is type("") else fschema
    myobj = load_yaml(finput) if type(finput) is type("") else finput
    DefaultValidatingDraft7Validator(yaml_schema).validate(myobj)
    return myobj


if __name__ == '__main__':
    path2yaml = Path(__file__).parent.parent.parent / "models" / "DTU_10MW" / "Madsen2019" / "Madsen2019_10.yaml"
    path2schema = Path(__file__).parent.parent / "models" / 'defaults' / "OTCD_schema.yaml"
    out = validate_with_defaults(path2yaml, path2schema)
    print(out)
