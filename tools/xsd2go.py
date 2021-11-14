from elementpath.datatypes import string
import xmlschema as xsd

def capitalize(str):
    return str[:1].upper() + str[1:]

def write_types(schema, go):
    schema = xsd.XMLSchema(schema)
    f = open(go, "w")
    f.write("package main\n\n")
    for type in schema.complex_types:
        f.write("type Xs" + type.local_name + " struct {\n")
        for elem in type.content.iter_elements():
            if elem.max_occurs == 0:
                continue
            row = "  " + capitalize(elem.local_name) + " "
            if elem.parent.model == 'choice' or elem.min_occurs == 0 and elem.max_occurs == 1:
                row += "*"
            if elem.max_occurs == None or elem.max_occurs > 1:
                row += "[]"
            if elem.type.has_complex_content():
                row += "Xs" + elem.type.local_name
            else:
                row += "string"
            row += ' `xml:"' + elem.local_name + '"`'
            f.write(row + "\n")
        f.write("}\n\n")
    f.close()

write_types("UCH758Model.xsd", "uch_model.go")
write_types("UCH758Load.xsd", "uch_load.go")
