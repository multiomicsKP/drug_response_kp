import os
import csv
import json


def verify_header_line(line):

    expected_header_line = ['Subject', 'Subject_Ensembl_gene_ID', 'Subject_NCBI_Gene_ID', 'Subject_Approved_symbol', 'Subject_Category', 'Object', 'Object_name', 'Object_id', 'Object_Category', 'Predicate', 'Edge_attribute_Subject_Modifier', 'Edge_attribute_Object_Modifier', 'Edge_attribute_method', 'Edge_attribute_Pvalue', 'Edge_attribute_evidence_type', 'Edge_attribute_evidence_value', 'Edge_attribute_sample_size', 'Edge_attribute_sample_orign', 'Edge_attribute_MONDO_ID', 'Edge_attribute_DataResource', 'Edge_attribute_Publication', 'Edge_attribute_Provider']
    buf = f"Header line: {line}\n"

    buf += "Expected == Observed\n"
    buf += "----------------------------------------------------\n"
    counter = 0
    observed_difference = False
    for column_name in expected_header_line:
        if counter < len(line):
            observed_name = line[counter]
        else:
            observed_name = '??'
        operator = '!='
        prefix = '  OK     '
        if column_name != observed_name:
            operator = '!='
            prefix = 'MISMATCH '
            observed_difference = True
        buf += f"{prefix} {column_name}  {operator}  {observed_name}\n"
        counter += 1

    if observed_difference:
        print(buf)
        raise Exception("Please ensure that the file is correct or update the parser to match the data")


def load_file(filename_path):
    print(f"INFO: Reading {filename_path}")
    with open(filename_path) as infile:

        reader = csv.reader(infile, delimiter=',')
        first_line = True

        # Get edge data
        for line in reader:

            if first_line:
                verify_header_line(line)
                first_line = False
                continue

            print(line)

            subject = {
                "id": line[1],
                "name": line[0],
                "type": 'biolink:' + line[4]
            }

            object_ = {
                "id": line[7],
                "name": line[6],
                "type": 'biolink:' + line[8]
            }

            edge_attributes = []
            edge_attributes.append(
                {
                    "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                    "attribute_type_id": "biolink:?????",
                    "description": "????",
                    "value": line[13],
                    "value_type_id": "biolink:t-test"   # made this up
                }
            )

            association = {
                "edge_label": line[9],
                "edge_attributes": edge_attributes
            }

            # Yield subject, predicate, and object properties
            yield {
                "_id": '-'.join([line[1], line[7], line[9], line[13]]),
                "subject": subject,
                "association": association,
                "object": object_
            }


def load_data(data_folder):
    filename_path = os.path.join(data_folder, "Table_DrugResponse_KP.csv")
    for row in load_file(filename_path):
        yield row


def main():
    counter = 0
    for row in load_data('.'):
        print(json.dumps(row, sort_keys=True, indent=2))
        counter += 1
        if counter >= 2:
            break


if __name__ == "__main__":
    main()
