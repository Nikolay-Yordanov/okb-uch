import xmlschema as xsd
import argparse

def capitalize(str):
    return str[:1].upper() + str[1:]

def write_types(schema_name, go, skip_deps=False):
    schema = xsd.XMLSchema(schema_name)
    f = open(go, "w")
    f.write("package main\n\n")
    for type in schema.complex_types:
        if skip_deps and type.schema.name != schema_name:
            continue
        f.write("// " + type.annotation.documentation[0].text + "\n")
        f.write("type Xs" + type.local_name + " struct {\n")
        for attr in type.attributes:
            row = "  " + capitalize(attr) + " *string " + '`xml:"' + attr + ',attr,omitempty"`'
            f.write(row + "\n")
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
            row += ' `xml:"' + elem.local_name + ',omitempty"`'
            f.write(row + "\n")
        f.write("}\n\n")
    f.close()

ap = argparse.ArgumentParser()

ap.add_argument("-x", "--xsd", required=False,
   help="XSD Schema to parse", default="UCH758Load.xsd")
ap.add_argument("-o", "--output", required=False,
   help="Filename to write result into", default="uch.go")
ap.add_argument("-s", "--shallow", required=False,
   help="Parse root schema only", action="store_true", default=False)
args = vars(ap.parse_args())

write_types(args['xsd'], args['output'], args['shallow'])
