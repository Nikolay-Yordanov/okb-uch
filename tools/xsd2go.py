import xmlschema as xsd
import argparse

files = {}
ifaces = ""
vmt = ["load", "validate"]


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

def write_func_decl(name):
    files["uch_func"].write("type {}Func func(ctx *Context) error\n\n".format(name))
    for fname in vmt:
        files["uch_func"].write("func (this {}) {}(ctx *Context) error {{ return nil }}\n\n".format(name, fname))

def format_vmt_init():
    format = ""
    for fname in vmt:
        format += "  this._{0} = this.{0}\n".format(fname)
    return format

def format_start_func(name):
    return "func (this {0}) {0}{{1}}(ctx *Context) error {{{{\n".format(name)

def format_end_func():
    return "  return nil\n}}\n\n"

def format_body(name, fname, optional, multi):
    format = ""
    if multi:
        format += \
            "  for _, v := range this.{0} {{{{\n"\
            "    v.{1}(ctx)\n"\
            "  }}}}\n".format(name, fname)
    elif optional:
        format += \
            "  if this.{0} != nil {{{{\n"\
            "    this.{0}.{1}(ctx)\n"\
            "  }}}}\n".format(name, fname)
    else:
        format += "  this.{0}.{1}(ctx)\n".format(name, fname)
    return format

def write_vmt(name):
    for fname in vmt:
        files["uch"].write("  _{} {}Func\n".format(fname, name))
    files["uch"].write("}\n\n")

def write_types(schema_name, skip_deps=False, interfaces=False):
    schema = xsd.XMLSchema(schema_name)
    init_file('uch')
    init_file('uch_func')
    for type in schema.complex_types:
        if skip_deps and type.schema.name != schema_name:
            continue
        write_all("// " + type.annotation.documentation[0].text + "\n")
        type_name = "Xs" + type.local_name
        write_struct(type_name)
        write_func_decl(type_name)
        format_start = format_start_func(type_name)
        # It's for collecting lines of the function body
        format = ""
        # Have to collect body for init function separately because there direct Xs...Init functions are called instead of through vmt
        format_init = ""
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
                format_init += format_body(field_name, tname+"Init", optional, multi)
                format += format_body(field_name, "_{0}", optional, multi)
        write_vmt(type_name)
        files["uch_func"].write((format_start + format_vmt_init() + format_init + format_end_func()).format("init", "Init"))
        for fname in vmt:
            files["uch_func"].write((format_start + format + format_end_func()).format(fname, capitalize(fname)))
    close_files()

ap = argparse.ArgumentParser()

ap.add_argument("-x", "--xsd", required=False,
    help="XSD Schema to parse", default="UCH758Load.xsd")
ap.add_argument("-s", "--shallow", required=False,
    help="Parse root schema only", action="store_true", default=False)
args = vars(ap.parse_args())

write_types(args['xsd'], args['shallow'])
