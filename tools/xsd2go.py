import xmlschema as xsd
import argparse

files = {}
ifaces = ""

def capitalize(str):
    return str[:1].upper() + str[1:]

def init_file(fname):
    files[fname] = open(fname+".go", "w")
    files[fname].write("package main\n\n")

def close_files():
    for f in files.values():
        f.close()

def write_all(s):
    for f in files.values():
        f.write(s)

def write_struct(name):
    files["uch"].write("type {} struct {{\n".format(name))

def write_attr(name, xname):
    files["uch"].write("  {} *string `xml:""' + {} + ',attr,omitempty""`\n".format(name, xname))

def write_field(name, xname, tname, optional, multi):
    row = "  " + name + " "
    if multi:
        row += "[]"
    elif optional:
        row += "*"
    row += tname
    row += ' `xml:"' + xname + ',omitempty"`'
    files["uch"].write(row + "\n")

def write_init_func(name):
    files["uch_init"].write("type {}Load func(ctx *Context) error\n\n".format(name))
    files["uch_init"].write("func (this {}) load(ctx *Context) error {{ return nil }}\n\n".format(name))
    files["uch_init"].write("func (this {}) init(ctx *Context) error {{\n".format(name))
    files["uch_init"].write("  this._load = this.load\n".format(name))

def write_end_func():
    files["uch_init"].write("  return nil\n")

def write_body(name, fname, optional, multi):
    if multi:
        files["uch_init"].write(
            "  for _, v := range this.{} {{\n"
            "    v.{}(ctx)\n"
            "  }}\n".format(name, fname))
    elif optional:
        files["uch_init"].write(
            "  if this.{0} != nil {{\n"
            "    this.{0}.{1}(ctx)\n"
            "  }}\n".format(name, fname))
    else:
        files["uch_init"].write("  this.{}.{}(ctx)\n".format(name, fname))

def write_vmt(name):
    files["uch"].write("  _load {0}Load\n".format(name))

def write_types(schema_name, skip_deps=False, interfaces=False):
    schema = xsd.XMLSchema(schema_name)
    init_file('uch')
    init_file('uch_init')
    for type in schema.complex_types:
        if skip_deps and type.schema.name != schema_name:
            continue
        write_all("// " + type.annotation.documentation[0].text + "\n")
        type_name = "Xs" + type.local_name
        write_struct(type_name)
        write_init_func(type_name)
        for attr in type.attributes:
            write_attr(capitalize(attr), attr)
        for elem in type.content.iter_elements():
            field_name = capitalize(elem.local_name)
            if elem.max_occurs == 0:
                continue
            optional = (elem.parent.model == 'choice' or elem.min_occurs == 0 and elem.max_occurs == 1)
            multi = (elem.max_occurs == None or elem.max_occurs > 1)
            if elem.type.has_complex_content():
                tname = "Xs" + elem.type.local_name
            else:
                tname  ="string"
            write_field(field_name, elem.local_name, tname, optional, multi)
            if elem.type.has_complex_content():
                write_body(field_name, "init", optional, multi)
                write_body(field_name, "_load", optional, multi)
        write_vmt(type_name)
        write_end_func()
        write_all("}\n\n")
    close_files()

ap = argparse.ArgumentParser()

ap.add_argument("-x", "--xsd", required=False,
    help="XSD Schema to parse", default="UCH758Load.xsd")
ap.add_argument("-s", "--shallow", required=False,
    help="Parse root schema only", action="store_true", default=False)
args = vars(ap.parse_args())

write_types(args['xsd'], args['shallow'])
