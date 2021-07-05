import os
import jsonschema as json
import yaml
    
    

#============ Utils ==================================================================
#making sure that we prepend "./" to a filename if provided in relative path
def arg_to_path(args,key):
    path = getattr(args,key) if key in args else ""
    if path != "" and path[0] != "." and path[0] != os.sep:
        path = "." + os.sep + path
    return path

#============= COPY PASTE FROM WEIS validation.py ====================================
# ---------------------
def load_yaml(fname_input):
    if not fname_input:
        return {}
    with open(fname_input, "r", encoding="utf-8") as f:
        data = f.read()
        input_yaml = yaml.load(data, Loader=yaml.FullLoader)
        # input_yaml = ry.load(f, Loader=ry.Loader)
    return input_yaml


def write_yaml(instance, foutput):
    # Write yaml with updated values
    # yaml = ry.YAML()
    # yaml.default_flow_style = None
    # yaml.width = float("inf")
    # yaml.indent(mapping=4, sequence=6, offset=3)
    # yaml.allow_unicode = False
    with open(foutput, "w", encoding="utf-8") as f:
        yaml.dump(instance, f)


# ---------------------
# See: https://python-jsonschema.readthedocs.io/en/stable/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance
def extend_with_default(validator_class):
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
    yaml_schema = load_yaml(fschema) if type(fschema) == type("") else fschema
    myobj = load_yaml(finput) if type(finput) == type("") else finput
    json.Draft7Validator(yaml_schema).validate(myobj)
    return myobj


def validate_with_defaults(finput, fschema):
    yaml_schema = load_yaml(fschema) if type(fschema) == type("") else fschema
    myobj = load_yaml(finput) if type(finput) == type("") else finput
    DefaultValidatingDraft7Validator(yaml_schema).validate(myobj)
    return myobj

#===================================================================================


if __name__ == '__main__':
    # path2yaml   = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ))) + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "IEA-10-198-RWT" + os.sep + "IEA-10-198-RWT.yaml"
    path2yaml   = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ))) + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep + "Madsen2019_10.yaml"
    path2schema = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ))) + os.sep + "models" + os.sep + 'defaults' + os.sep + "OTCD_schema.yaml"

    # path2yaml   = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ))) + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "dummy.yaml"
    # path2schema = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ))) + os.sep + "models" + os.sep + 'defaults' + os.sep + "dummy_schema.yaml"

    out = validate_with_defaults(path2yaml,path2schema)
    print(out)

    #NOTE: need to revert the coordinates for PGL, take the opposite of the twist angle

    # #test or writing:
    # pth = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))+'/test.yaml' 
    # write_yaml(out, pth)
    
    # out2 = validate_with_defaults(path2yaml,path2schema)
    # print(out2)


