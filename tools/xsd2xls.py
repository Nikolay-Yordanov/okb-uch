import xlsxwriter
import xmlschema as xsd

row = 0
workbook = None
worksheet = None
styles = {}

def get_doc(node):
    return node.annotation.documentation[0].text

def get_indent(depth):
    return '   ' * depth * 2

def get_multiplicity(node):
    return str(node.min_occurs) + '..' + str(node.max_occurs)

def process_elem(parent, depth, limit):
    if depth == limit:
        return
    for elem in parent.type.content.iter_elements():
        write_row(
            get_indent(depth) + elem.local_name,
            get_doc(elem),
            get_multiplicity(elem),
            get_doc(elem.type)
        )
        if elem.type.has_complex_content():
            process_elem(elem, depth + 1, limit)

def write_row(*cols, style='normal'):
    global worksheet, row
    coln = 0
    for col in cols:
        worksheet.write(row, coln, col, styles[style])
        coln += 1
    row += 1

def init_workbook():
    global workbook, styles
    workbook = xlsxwriter.Workbook('UCH758.xlsx')
    styles['bold'] = workbook.add_format({'bold': True, 'text_wrap': True})
    styles['normal'] = workbook.add_format({'bold': False, 'text_wrap': True})
    styles['title'] = workbook.add_format({'bold': True})

def close_workbook():
    workbook.close()

def init_worksheet(name):
    global workbook, worksheet, row
    row = 0
    worksheet = workbook.add_worksheet(name)
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 40)
    worksheet.set_column('C:C', 8)
    worksheet.set_column('D:D', 60)

def write_sheet(title, schema, section, limit):
    row = 0
    init_worksheet(title)
    schema=xsd.XMLSchema(schema)
    write_row(schema.annotations[section].documentation[0].text, style='title')
    write_row("xml", "описание", "множ.", "тип/формат", style='title')
    root=schema.elements[title]
    write_row(root.local_name, get_doc(root))
    process_elem(root, 0, limit)

init_workbook()
write_sheet("package", "UCH758Load.xsd", 0, 3)
write_sheet("personEvents", "UCH758Load.xsd", 1, 2)
write_sheet("orgEvents", "UCH758Load.xsd", 2, 2)
write_sheet("personCreditHistory", "UCH758Model.xsd", 0, 5)
write_sheet("orgCreditHistory", "UCH758Model.xsd", 1, 5)
close_workbook()
