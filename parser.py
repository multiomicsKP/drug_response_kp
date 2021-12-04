import os
import csv
import json

distinction_type = {
        "Genetic variants": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "biolink:GeneToDrugAssociation", # made up but similar to real GeneToDiseaseAssociation
                "description": "Sensitivity to the drug is associated with genetic variants of the gene",
                "value": "biolink:GeneHasVariantThatContributesToDrugSensitivityAssociation", # made up but similar to real GeneHasVariantThatContributesToDiseaseAssociation
                "value_type_id": "biolink:id"
        },
        "Expression": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "biolink:GeneToDrugAssociation", # made up but similar to real GeneToDiseaseAssociation
                "description": "Sensitivity to the drug is associated with expression of the gene",
                "value": "biolink:GeneHasExpressionThatContributesToDrugSensitivityAssociation", # made up but similar to real GeneHasVariantThatContributesToDiseaseAssociation
                "value_type_id": "biolink:id"
        }
}

concentration_endpoint = {
        "IC50": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "BAO:0002162", # concentration response endpoint -- http://www.bioassayontology.org/bao#BAO_0002162
                "description": "Method used to quantify the strength of the association is IC50",
                "value": "BAO:0000190", # IC50 -- http://www.bioassayontology.org/bao#BAO_0000190
                "value_type_id": "biolink:id"
        },
        "AUC": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "BAO:0002162", # concentration response endpoint -- http://www.bioassayontology.org/bao#BAO_0002162
                "description": "Method used to quantify the strength of the association is AUC",
                "value": "BAO:0002120", # AUC -- http://www.bioassayontology.org/bao#BAO_0002120
                "value_type_id": "biolink:id"
        }
}

correlation_statistic = {
        "T-test": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "NCIT:C53236", # Correlation Test -- http://purl.obolibrary.org/obo/NCIT_C53236
                "description": "t-test was used to compute the p-value for the association",
                "value": "NCIT:C53231", # t-Test -- http://purl.obolibrary.org/obo/NCIT_C53231
                "value_type_id": "biolink:id"
        },
        "Spearman_correlation": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "NCIT:C53236", # Correlation Test -- http://purl.obolibrary.org/obo/NCIT_C53236
                "description": "Spearman Correlation Test was used to compute the p-value for the association",
                "value": "NCIT:C53249", # Spearman Correlation Test -- http://purl.obolibrary.org/obo/NCIT_C53249
                "value_type_id": "biolink:id"
        }
}





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
        counter = 0
        record_ids = {}

        # Get edge data
        for line in reader:

            if first_line:
                verify_header_line(line)
                first_line = False
                continue

            #print(line)


            counter += 1

            subject_id = line[1]
            #if subject_id.startswith('ENSG0'):
            #    subject_id = 'ENSEMBL:' + subject_id
            #elif subject_id.startswith('ENSEMBL:'):
            #    pass
            #elif subject_id == '':
            #    print(f"ERROR: Empty CURIE for subject at line {counter}")
            #    continue
            #else:
            #    raise Exception(f"subject_id {subject_id} does not begin with ENSG0 or ENSEMBL: at line {counter}")

            components = subject_id.split(':')
            if len(components) == 2:
                extra_property = components[0]
            else:
                raise Exception(f"Unable to split {subject_id} on a single colon at line {counter}")

            subject = {
                "id": subject_id,
                "name": line[0],
                extra_property: subject_id,
                "type": 'biolink:' + line[4]
            }

            object_category = line[8]
            if object_category == 'ChemicalSubstance':
                object_category = 'SmallMolecule'

            object_id = line[7]
            if object_id.startswith('CHEMBL:'):
                object_id = 'CHEMBL.COMPOUND:' + object_id.split(':')[1]
            elif object_id.startswith('CHEMBL'):
                object_id = 'CHEMBL.COMPOUND:' + object_id
            elif object_id.startswith('CHEBI:'):
                pass
            elif object_id.startswith('HMS_LINCS_ID:'):
                pass
            elif object_id.startswith('CID:'):
                pass
            elif object_id.startswith('PUBCHEM:'):
                pass
            else:
                raise Exception(f"object_id '{object_id}' does not begin with CHEMBL at line {counter}")

            components = object_id.split(':')
            if len(components) == 2:
                extra_property = components[0]
            else:
                raise Exception(f"Unable to split {object_id} on a single colon at line {counter}")

            object_ = {
                "id": object_id,
                "name": line[6],
                extra_property: object_id,
                "type": 'biolink:' + object_category
            }

            edge_attributes = []

            # could be Genetic variants / Gene expression
            if line[10] in distinction_type:
                edge_attributes.append(distinction_type[line[10]])
            else:
                raise Exception(f"Column 10 has unexpected value {line[10]}")

            # could be IC50 / AUC
            if line[11] in concentration_endpoint:
                edge_attributes.append(concentration_endpoint[line[11]])
            else:
                raise Exception(f"Column 11 has unexpected value {line[11]}")

            # could be t-test or Spearman
            if line[12] in correlation_statistic:
                attributes = correlation_statistic[line[12]]
            else:
                raise Exception(f"Column 12 has unexpected value {line[12]}")

            # p-value
            edge_attributes.append(
                {
                    "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                    "attribute_type_id": "EDAM:data_0951", # statistical estimate score -- http://edamontology.org/data_0951
                    "description": "Confidence metric for the association",
                    "value": float(line[13]),
                    "value_type_id": "EDAM:data_1669",   # P-value -- http://edamontology.org/data_1669
                    "attributes": attributes
                }
            )

            # sample size
            edge_attributes.append(
                {
                    "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                    "attribute_type_id": "GECKO:0000106", # sample size - http://purl.obolibrary.org/obo/GECKO_0000106
                    "description": "Sample size used to compute the correlation",
                    "value": int(line[16]),
                }
            )

            # disease context
            edge_attributes.append(
                {
                    "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                    "attribute_type_id": "biolink:has_disease_context", # I made this up, but similar to biolink:has_population_context
                    "description": "Disease context for the gene-drug sensitivity association",
                    "value": line[18],
                    "value_type_id": "biolink:id"
                }
            )

            # GDSC
            pmid = line[20]
            pmid = pmid.replace(' ', '')
            edge_attributes.append(
                {
                    "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                    "attribute_type_id": "biolink:Dataset",
                    "description": "Dataset used to compute the association",
                    "value": line[19],
                    "value_type_id": None,
                    "attributes": 
                        {
                            "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                            "attribute_type_id": "biolink:Publication",
                            "description": "Publication describing the dataset used to compute the association",
                            "value": pmid,
                            "value_type_id": "biolink:id"
                    }
                }
            )

            association = {
                "edge_label": line[9],
                "edge_attributes": edge_attributes
            }

            #if counter / 10000 == int(counter / 10000):
            #    print(f"{counter}.. ", end='', flush=True)

            #### Create a unique record_id, verify that it's unique, and then create a hash to make it shorter
            record_id = 'DRKP-' + '-'.join( [ subject_id, line[9], object_id, line[18], line[13] ] )
            if record_id in record_ids:
                record_ids[record_id] += 1
                print(f"ERROR: Duplicate record id {record_id} found on line {counter}")
                record_id += f"-{record_ids[record_id]}"
            else:
                record_ids[record_id] = 1

            # Yield subject, predicate, and object properties
            yield {
                "_id": record_id,
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
    verbose = False
    for row in load_data('.'):
        if verbose:
            print(json.dumps(row, sort_keys=True, indent=2))
        counter += 1
        #if counter >= 2:
        #    break


if __name__ == "__main__":
    main()
