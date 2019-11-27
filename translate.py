import click
from lxml import etree
import xlrd, xlwt, mmap
from xml.dom import minidom

nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}

def XLSDictReader(f, sheet_index=0):
    book    = xlrd.open_workbook(file_contents=mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ))
    sheet   = book.sheet_by_index(sheet_index)
    headers = dict( (i, sheet.cell_value(0, i) ) for i in range(sheet.ncols) )
    return ( dict( (headers[j], sheet.cell_value(i, j)) for j in headers ) for i in range(1, sheet.nrows) )


def get_text(element):
    if element is None: return ""
    return element.text


@click.group()
def main():
   pass


@main.command()
@click.option('--existing_codelist_filename', help="The filename of the existing XML codelists file, e.g. 'Sector.xml'.")
@click.option('--output_filename', help="The output filename of the new XML codelists file incorporating the translations.")
@click.option('--new_translation_filename', help="The filename of the Excel translation of the existing codelists file.")
@click.option('--lang', help="The language of the translations file in lowercase, e.g. 'fr' for French.")
def merge_translations(existing_codelist_filename, output_filename, new_translation_filename, lang):
    """Merge translations from a provided Excel translations
    file into an existing XML file."""
    parser = etree.XMLParser(remove_blank_text=True)
    codelist_xml_file = open(existing_codelist_filename)
    codelist_xml = etree.parse(codelist_xml_file, parser)

    translated_file = open(new_translation_filename, "r")
    codes = XLSDictReader(translated_file)

    for one_code in codes:
        the_code = codelist_xml.xpath("/codelist/codelist-items/codelist-item[code/text()='{}']".format(one_code["code"]))[0]

        if one_code["name"]:
            new_name = the_code.find('name/narrative[@xml:lang="{}"]'.format(lang), namespaces=nsmap)
            if new_name is None:
                new_name = etree.SubElement(the_code.find('name'), "narrative")
                new_name.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
            new_name.text = one_code["name"]

        if one_code["description"]:
            new_description = the_code.find('description/narrative[@xml:lang="{}"]'.format(lang), namespaces=nsmap)
            if new_description is None:
                new_description = etree.SubElement(the_code.find('description'), "narrative")
                new_description.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
            new_description.text = one_code["description"]

    codelist_xml_file = open(output_filename, "w")
    codelist_xml_file.write(
        minidom.parseString(etree.tostring(codelist_xml)).toprettyxml(indent="    ")
    )


@main.command()
@click.option('--existing_codelist_filename', help="The filename of the existing XML codelists file, e.g. 'Sector.xml'.")
@click.option('--output_filename', help="The output filename of the Excel translations into the desired language.")
@click.option('--lang', help="The language of the translations file in lowercase, e.g. 'fr' for French.")
def generate_translations(existing_codelist_filename, output_filename, lang):
    """Generate an Excel translations file from an existing
    XML file"""
    parser = etree.XMLParser(remove_blank_text=True)
    codelist_xml_file = open(existing_codelist_filename)
    codelist_xml = etree.parse(codelist_xml_file, parser)

    wb = xlwt.Workbook()
    sheet = wb.add_sheet('Sheet 1')
    sheet.write(0,0,'code')
    sheet.write(0,1,'name')
    sheet.write(0,2,'description')
    for i, code in enumerate(codelist_xml.xpath("/codelist/codelist-items/codelist-item")):
        sheet.write(i+1, 0, get_text(code.find('code')))
        sheet.write(i+1, 1, get_text(code.find('name/narrative[@xml:lang="{}"]'.format(lang), namespaces=nsmap)))
        sheet.write(i+1, 2, get_text(code.find('description/narrative[@xml:lang="{}"]'.format(lang), namespaces=nsmap)))
    wb.save(output_filename)


if __name__ == '__main__':
    main()
