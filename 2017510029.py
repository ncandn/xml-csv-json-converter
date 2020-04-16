import csv
import codecs
import os
import io
from lxml import etree as etlxml
from xml.etree import ElementTree as etxml
import json
from xml.dom import minidom
import sys

# CSV TO XML OPERATION
def csv2xml(input_file, output_file):
    # File operations.
    csv_file = input_file
    fcsv = io.open(csv_file, 'r', encoding='UTF-8')
    csv_lines = csv.reader(fcsv, delimiter=';')
    # Ignoring the first line with a counter.
    line_count = 1
    fxml = open(output_file, 'w', encoding='UTF-8')
    # Creating a root element.
    root = etxml.Element("departments")
    # Unifying same universities under one category.
    temp_university = ""
    try:
        while True:
            line = next(csv_lines)
            # Implementation of the first line expection.
            if line_count != 1:
                # University category.
                if temp_university != line[1]:
                    # Adding child and setting attributes to the root.
                    child = etxml.SubElement(root, "university")
                    child.set("name", line[1])
                    child.set("uType", line[0])
                    temp_university = line[1]
                # Adding child to the previously created child item and setting attributes.
                item = etxml.SubElement(child, "item")
                item.set("faculty", line[2])
                item.set("id", line[3])

                sub_item1 = etxml.SubElement(item, "name")
                # Blank space controls and corrections.
                if line[5].lower() == "":
                    sub_item1.set("lang", "tr")
                else:
                    sub_item1.set("lang", "en")
                if line[6].lower() == "":
                    sub_item1.set("second", "no")
                else:
                    sub_item1.set("second", "yes")
                sub_item1.text = line[4]
                # Adding each elements and attributes if exist.
                sub_item2 = etxml.SubElement(item, "period")
                sub_item2.text = line[8]

                sub_item3 = etxml.SubElement(item, "quota")
                sub_item3.set("spec", line[11])
                sub_item3.text = line[10]

                sub_item4 = etxml.SubElement(item, "field")
                sub_item4.text = line[9]

                sub_item5 = etxml.SubElement(item, "last_min_score")
                sub_item5.set("order", line[12])
                if line[13] == '-' :
                    sub_item5.text = ''
                else:
                    sub_item5.text = line[13]

                sub_item6 = etxml.SubElement(item, "grant")
                sub_item6.text = line[7]

            else:
                line_count = line_count + 1
    except StopIteration:
        test = 0
    # Pretty print and output operations.
    outfile = etxml.tostring(root)
    outfile_pretty = minidom.parseString(outfile).toprettyxml()
    fxml.write(outfile_pretty)
    # Closure of the files.
    fxml.close()
    fcsv.close()

# XML TO CSV OPERATION
def xml2csv(input_file, output_file):
    # Parsing the tree from the xml file and getting the root element.
    tree = etxml.parse(input_file)
    root = tree.getroot()
    newcsv = open(output_file, 'w', encoding='UTF-8', newline='')
    csvwrite = csv.writer(newcsv, delimiter=';')
    # Pre-made headers/titles.
    csv_titles = ['ÜNİVERSİTE_TÜRÜ', 'ÜNİVERSİTE', 'FAKÜLTE', 'PROGRAM_KODU', 'PROGRAM', 'DİL', 'ÖĞRENİM_TÜRÜ', 'BURS',
                  'ÖĞRENİM_SÜRESİ', 'PUAN_TÜRÜ',
                  'KONTENJAN', 'OKUL_BİRİNCİSİ_KONTENJANI', 'GEÇEN_YIL_MİN_SIRALAMA', 'GEÇEN_YIL_MİN_PUAN']
    csvwrite.writerow(csv_titles)

    for child in root:
        # Creating a temp list for unified the universities.
        templist = []
        templist.append(child.attrib.get('uType'))
        templist.append(child.attrib.get('name'))
        # Second loop to access the items of a university.
        for item in child:
            # Creating the items and appending them to the corresponding university.
            university = []
            university += templist
            university.append(item.attrib.get('faculty'))
            university.append(item.attrib.get('id'))
            university.append(item.find('name').text)
            # Controls for several attributes.
            if item.find('name').get('lang').lower() == "en":
                university.append("İngilizce")
            else:
                university.append("")
            if item.find('name').get('second') == "yes":
                university.append("İkinci Öğretim")
            else:
                university.append("")
            university.append(item.find('grant').text)
            university.append(item.find('period').text)
            university.append(item.find('field').text)
            university.append(item.find('quota').text)
            university.append(item.find('quota').get('spec'))
            university.append(item.find('last_min_score').get('order'))
            university.append(item.find('last_min_score').text)

            csvwrite.writerow(university)
            university.clear()

    newcsv.close()

# XML TO JSON OPERATION
def xml2json(input_file, output_file):
    # Parsing the xml file and getting its root.
    tree = etxml.parse(input_file)
    root = tree.getroot()
    fjson = open(output_file, 'w', encoding='UTF-8')
    # The cumulative list for printing that will contain all information.
    last_dict = []
    # Control flag for ignoring the first line. (header line)
    firstline_flag = True

    for child in root:
        # Filling the first item in the dictionary.
        # This used to cause a problem where the first element of the dictionary was empty.
        dept_dict = {'university name': child.attrib.get('name'), 'uType': child.attrib.get('uType'), 'items': [
            {'faculty': child.find('item').attrib.get('faculty'),
             'department': [
                 {'id': child.find('item').attrib.get('id'), 'name': child.find('item').find('name').text,
                  'lang': child.find('item').find('name').get('lang'),
                  'second': child.find('item').find('name').get('second'),
                  'period': child.find('item').find('period').text,
                  'spec': child.find('item').find('quota').get('spec'),
                  'quota': child.find('item').find('quota').text, 'field': child.find('item').find('field').text,
                  'last_min_score': child.find('item').find('last_min_score').text,
                  'last_min_order': child.find('item').find('last_min_score').get('order'),
                  'grant': child.find('item').find('grant').text}]}]}
        # Second loop to unify the universities.
        for item in child:
            # Checking if the items are headers.
            if not firstline_flag:
                mid_dict = {'faculty': item.attrib.get('faculty'),
                            'department': [
                                {'id': item.attrib.get('id'), 'name': item.find('name').text,
                                 'lang': item.find('name').get('lang'), 'second': item.find('name').get('second'),
                                 'period': item.find('period').text, 'spec': item.find('quota').get('spec'),
                                 'quota': item.find('quota').text, 'field': item.find('field').text,
                                 'last_min_score': item.find('last_min_score').text,
                                 'last_min_order': item.find('last_min_score').get('order'),
                                 'grant': item.find('grant').text}]}
                dept_dict['items'].append(mid_dict)
            firstline_flag = False
        last_dict.append(dept_dict)
    # JSON pretty print.
    fjson.write(json.dumps(last_dict, indent=3, sort_keys=False, ensure_ascii=False))
    fjson.close()

# JSON TO XML OPERATION
def json2xml(input_file, output_file):
    # File operations.
    json_file = input_file
    fjson = io.open(json_file, 'r', encoding='UTF-8')
    fxml = open(output_file, 'w', encoding='UTF-8')
    root = etxml.Element("departments")
    data = json.load(fjson)

    for item in data:
        # Creating the xml structure.
        # Dictionary values from the JSON file are fetched and used in xml tree functions.
        child = etxml.SubElement(root, "university")
        child.set("name", item['university name'])
        child.set("uType", item['uType'])
        for sub_item in item['items']:
            item = etxml.SubElement(child, "item")
            item.set("faculty", sub_item['faculty'])
            for elem in sub_item['department']:
                item.set("id", elem['id'])
                sub_item1 = etxml.SubElement(item, "name")
                sub_item1.set("lang", elem['lang'])
                sub_item1.set("second", elem['second'])
                sub_item1.text = elem['name']

                sub_item2 = etxml.SubElement(item, "period")
                sub_item2.text = elem['period']

                sub_item3 = etxml.SubElement(item, "quota")
                sub_item3.set("spec", elem['spec'])
                sub_item3.text = elem['quota']

                sub_item4 = etxml.SubElement(item, "field")
                sub_item4.text = elem['field']

                sub_item5 = etxml.SubElement(item, "last_min_score")
                sub_item5.set("order", elem['last_min_order'])
                sub_item5.text = elem['last_min_score']

                sub_item6 = etxml.SubElement(item, "grant")
                sub_item6.text = elem['grant']
    # Pretty printing.
    outfile = etxml.tostring(root)
    outfile_pretty = minidom.parseString(outfile)
    outfile_pretty = outfile_pretty.toprettyxml()
    fxml.write(outfile_pretty)
    fxml.close()
    fjson.close()

# CSV TO JSON OPERATION
def csv2json(input_file, output_file):
    # File operations.
    csv_file = input_file
    fcsv = io.open(csv_file, 'r', encoding='UTF-8')
    csv_lines = csv.reader(fcsv, delimiter=';')
    fjson = open(output_file, 'w', encoding='UTF-8')
    line_count = 1
    # Cumulative list as mentioned before.
    last_dict = []

    for line in csv_lines:
        if line_count != 1:
            temp_university = line[1]
            # Replacing empty values with NULL.
            for i in range(len(line)):
                if line[i] == "":
                    line[i] = None
            # Pre-printing to evading empty printing issue.
            dept_dict = {'university name': line[1], 'uType': line[0], 'items': [
                {'faculty': line[2],
                 'department': [
                     {'id': line[3], 'name': line[4], 'lang': line[5], 'second': line[6], 'period': line[8],
                      'spec': line[11],
                      'quota': line[10], 'field': line[9], 'last_min_score': line[13], 'last_min_order': line[12],
                      'grant': line[7]}]}]}
            for line in csv_lines:
                # Replacing empty values with NULL.
                for i in range(len(line)):
                    if line[i] == "":
                        line[i] = None
                mid_dict = {'faculty': line[2],
                            'department': [
                                {'id': line[3], 'name': line[4], 'lang': line[5], 'second': line[6],
                                 'period': line[8], 'spec': line[11],
                                 'quota': line[10], 'field': line[9], 'last_min_score': line[13],
                                 'last_min_order': line[12],
                                 'grant': line[7]}]}
                # Layered dictionary usage for unifying universities.
                dept_dict['items'].append(mid_dict)
                if temp_university != line[1]:
                    break
            last_dict.append(dept_dict)

        else:
            line_count = line_count + 1
    # Pretty print JSON.
    fjson.write(json.dumps(last_dict, indent=3, sort_keys=False, ensure_ascii=False))
    fjson.close()
    fcsv.close()

# JSON TO CSV OPERATION
def json2csv(input_file, output_file):
    # File operations.
    json_file = input_file
    fjson = io.open(json_file, 'r', encoding='UTF-8')
    newcsv = open(output_file, 'w', encoding='UTF-8', newline='')
    csvwrite = csv.writer(newcsv, delimiter=';')
    # Pre-made headers.
    csv_titles = ['ÜNİVERSİTE_TÜRÜ', 'ÜNİVERSİTE', 'FAKÜLTE', 'PROGRAM_KODU', 'PROGRAM', 'DİL', 'ÖĞRENİM_TÜRÜ', 'BURS',
                  'ÖĞRENİM_SÜRESİ', 'PUAN_TÜRÜ',
                  'KONTENJAN', 'OKUL_BİRİNCİSİ_KONTENJANI', 'GEÇEN_YIL_MİN_SIRALAMA', 'GEÇEN_YIL_MİN_PUAN']
    csvwrite.writerow(csv_titles)
    data = json.load(fjson)
    # Layered loop usage to reach items as different unions.
    for item in data:
        # Temporary list for universities as mentioned before.
        templist = []
        templist.append(item['uType'])
        templist.append(item['university name'])
        for sub_item in item['items']:
            university = []
            university += templist
            university.append(sub_item['faculty'])
            for elem in sub_item['department']:
                university.append(elem['id'])
                university.append(elem['name'])
                university.append(elem['lang'])
                university.append(elem['second'])
                university.append(elem['grant'])
                university.append(elem['period'])
                university.append(elem['field'])
                university.append(elem['quota'])
                university.append(elem['spec'])
                university.append(elem['last_min_order'])
                university.append(elem['last_min_score'])

            csvwrite.writerow(university)
            university.clear()
    # Closure of the files.
    fjson.close()
    newcsv.close()


def xsd_validation(input_file, output_file):
    fxml = etlxml.parse(input_file)
    root = fxml.getroot()
    xmlschema_fxml = etlxml.parse(output_file)
    xmlschema = etlxml.XMLSchema(xmlschema_fxml)
    fxml = etlxml.XML(etlxml.tostring(root))
    validation_result = xmlschema.validate(fxml)
    print(validation_result)
    xmlschema.assert_(fxml)


# Fetching arguments.
input_file = sys.argv[1]
output_file = sys.argv[2]
optype = sys.argv[3]
# Controlling operation options.
if optype == '1':
    in_extension = input_file.split('.')
    out_extension = output_file.split('.')
    if in_extension[-1] != 'csv' :
        print("False input extension.")
    elif out_extension[-1] != 'xml' :
        print("False output extension.")
    else:
        csv2xml(input_file, output_file)

elif optype == '2':
    in_extension = input_file.split('.')
    out_extension = output_file.split('.')
    if in_extension[-1] != 'xml' :
        print("False input extension.")
    elif out_extension[-1] != 'csv' :
        print("False output extension.")
    else:
        xml2csv(input_file, output_file)

elif optype == '3':
    in_extension = input_file.split('.')
    out_extension = output_file.split('.')
    if in_extension[-1] != 'xml' :
        print("False input extension.")
    elif out_extension[-1] != 'json' :
        print("False output extension.")
    else:
        xml2json(input_file, output_file)

elif optype == '4':
    in_extension = input_file.split('.')
    out_extension = output_file.split('.')
    if in_extension[-1] != 'json' :
        print("False input extension.")
    elif out_extension[-1] != 'xml' :
        print("False output extension.")
    else:
        json2xml(input_file, output_file)

elif optype == '5':
    in_extension = input_file.split('.')
    out_extension = output_file.split('.')
    if in_extension[-1] != 'csv':
        print("False input extension.")
    elif out_extension[-1] != 'json':
        print("False output extension.")
    else:
        csv2json(input_file, output_file)

elif optype == '6':
    in_extension = input_file.split('.')
    out_extension = output_file.split('.')
    if in_extension[-1] != 'json':
        print("False input extension.")
    elif out_extension[-1] != 'csv':
        print("False output extension.")
    else:
        json2csv(input_file, output_file)

elif optype == '7':
    in_extension = input_file.split('.')
    out_extension = output_file.split('.')
    if in_extension[-1] != 'xml':
        print("False input extension.")
    elif out_extension[-1] != 'xsd':
        print("False output extension.")
    else:
        xsd_validation(input_file, output_file)

else:
    print("False operation type.")

