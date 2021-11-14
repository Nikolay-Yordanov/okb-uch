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

def get_traits(node):
    max_occurs = node.max_occurs
    if max_occurs == None:
        max_occurs = 'many'
    traits = str(node.min_occurs) + '..' + str(max_occurs)
    if node.parent.model == 'choice':
        traits += '/choice'
    return traits


def process_elem(type, depth, limit, width):
    if depth == limit:
        return
    for elem in type.content.iter_elements():
        write_row(
            get_indent(depth) + elem.local_name,
            get_doc(elem),
            get_traits(elem),
            get_doc(elem.type),
            width=width
        )
        if elem.type.has_complex_content():
            process_elem(elem.type, depth + 1, limit, width)

def write_row(*cols, width=1, style='normal'):
    global worksheet, row
    coln = 0
    for col in cols:
        worksheet.write(row, coln, col, styles[style])
        coln += 1
        if coln == width:
            break
    if coln == 1 and width > 1:
        worksheet.merge_range(row, 0, row, width-1, cols[0], styles[style])
    row += 1

def init_workbook():
    global workbook, styles
    workbook = xlsxwriter.Workbook('UCH758.xlsx')
    styles['columns'] = workbook.add_format({'bold': True, 'bottom': 1})
    styles['normal'] = workbook.add_format({'bold': False, 'text_wrap': True, 'valign': 'top'})
    styles['title'] = workbook.add_format({'bold': True, 'bg_color': '#e0e0e0', 'align': 'center'})
    styles['root'] = workbook.add_format({'bold': True})

def close_workbook():
    workbook.close()

def init_worksheet(name, col_widths):
    global workbook, worksheet, row
    row = 0
    worksheet = workbook.add_worksheet(name)
    col = 0
    for w in col_widths:
        worksheet.set_column(col, col, w)
        col += 1

def write_sheet(title, schema, width, section, limit, *col_widths):
    row = 0
    schema = xsd.XMLSchema(schema)
    init_worksheet(title, col_widths)
    write_row(schema.annotations[section].documentation[0].text, width=width, style='title')
    write_row("xml", "описание", "множ./или", "тип/формат", width=width, style='columns')
    if schema.elements.get(title) != None:
        root = schema.elements[title]
        root_type = root.type
    else:
        root = schema.types[title]
        root_type = root
    write_row(root.local_name, get_doc(root), width=width, style='root')
    process_elem(root_type, 0, limit, width)

init_workbook()
write_sheet("package", "UCH758Load.xsd", 3, 0, 2, 32, 100, 14)
write_sheet("PersonEventType", "UCH758Load.xsd", 3, 1, 2, 32, 100, 14)
write_sheet("OrgEventType", "UCH758Load.xsd", 3, 2, 2, 32, 100, 14)
write_sheet("PersonCreditHistoryType", "UCH758Model.xsd", 4, 0, 5, 25, 40, 14, 80)
write_sheet("OrgCreditHistoryType", "UCH758Model.xsd", 4, 1, 5, 25, 40, 14, 80)
write_sheet("PersonReportType", "UCH758Report.xsd", 4, 0, 5, 25, 40, 14, 80)
write_sheet("OrgReportType", "UCH758Report.xsd", 4, 1, 5, 25, 40, 14, 80)
close_workbook()
