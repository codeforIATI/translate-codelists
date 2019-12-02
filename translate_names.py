import click
from lxml import etree
import xlrd, xlwt, mmap
from xml.dom import minidom
import re
import os

nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}

def XLSDictReader(f, sheet_index=0):
    book    = xlrd.open_workbook(file_contents=mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ))
    sheet   = book.sheet_by_index(sheet_index)
    headers = dict( (i, sheet.cell_value(0, i) ) for i in range(sheet.ncols) )
    return ( dict( (headers[j], sheet.cell_value(i, j)) for j in headers ) for i in range(1, sheet.nrows) )


def get_text(element):
    if element is None: return ""
    if element.text is None: return ""
    return element.text


# Thanks to https://infix.se/2007/02/06/gentlemen-indent-your-xml
def indent(elem, level=0):
    """Ensures the file is still indented with 4 spaces, as all
    the existing codelist files are."""
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for e in elem:
            indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "    "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


@click.group()
def main():
   pass


def filter_xml(codelist):
    return codelist.endswith(".xml")


def get_codelist_name(codelist_url):
    return re.match("http://reference.iatistandard.org/203/codelists/(.*)", codelist_url).group(1)


@main.command()
@click.option('--existing_codelist_folder', help="The filename of the existing XML codelists file, e.g. 'Sector.xml'.")
@click.option('--new_translation_filename', help="The filename of the Excel translation of the existing codelists file.")
def merge_translations(existing_codelist_folder, new_translation_filename):
    """Merge translations from a provided Excel translations
    file into an existing XML file."""
    parser = etree.XMLParser(remove_blank_text=True)
    translated_file = open(new_translation_filename, "r")
    codes = XLSDictReader(translated_file)
    codes_restructured = dict(map(lambda code: (get_codelist_name(code["url"]), code), codes))
    for codelist_filename in filter(filter_xml, os.listdir(existing_codelist_folder)):
        codelist_xml_file = open(os.path.join(existing_codelist_folder, codelist_filename), "r")
        codelist_xml = etree.parse(codelist_xml_file, parser)
        codelist_xml_file.close()

        codelist_name = codelist_xml.getroot().get("name")
        codelist_data = codes_restructured.get(codelist_name)
        if not codelist_data: continue

        for k, v in codelist_data.items():
            if k == 'url': continue
            if (v in ('', None)): continue
            el, lang = k.split("_")
            if codelist_xml.find("/metadata/{}".format(el)) is None:
                mk_group = etree.SubElement(codelist_xml.find("/metadata"), el)
            if lang != "en":
                cl_el = codelist_xml.find('/metadata/{}/narrative[@xml:lang="{}"]'.format(el, lang), namespaces=nsmap)
                if cl_el is None:
                    cl_el = etree.SubElement(codelist_xml.find("/metadata/{}".format(el)), "narrative")
                    cl_el.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
                if (get_text(cl_el).strip() != v.strip()):
                    cl_el.text = v
            else:
                cl_el = codelist_xml.xpath("//metadata/{}/narrative[not(@xml:lang)]".format(el), namespaces=nsmap)
                if len(cl_el) == 0:
                    cl_el = etree.SubElement(codelist_xml.find("/metadata/{}".format(el)), "narrative")
                    cl_el.text = v
                else:
                    if (get_text(cl_el[0]) != v.strip()):
                        cl_el[0].text = v

        indent(codelist_xml.getroot())
        outf = open(os.path.join(existing_codelist_folder, codelist_filename), 'w')
        outf.write("{}\n".format(etree.tostring(codelist_xml, encoding="unicode")))
        outf.close()

if __name__ == '__main__':
    main()
