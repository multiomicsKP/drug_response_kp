import os
import sys
import csv
import json

distinction_type = {
        "Genetic variants": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "biolink:GeneToDrugAssociation",  # made up but similar to real GeneToDiseaseAssociation
                "description": "Sensitivity to the drug is associated with genetic variants of the gene",
                "value": "biolink:GeneHasVariantThatContributesToDrugSensitivityAssociation",  # made up but similar to real GeneHasVariantThatContributesToDiseaseAssociation
                "value_type_id": "biolink:id"
        },
        "Expression": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "biolink:GeneToDrugAssociation",  # made up but similar to real GeneToDiseaseAssociation
                "description": "Sensitivity to the drug is associated with expression of the gene",
                "value": "biolink:GeneHasExpressionThatContributesToDrugSensitivityAssociation",  # made up but similar to real GeneHasVariantThatContributesToDiseaseAssociation
                "value_type_id": "biolink:id"
        }
}

concentration_endpoint = {
        "IC50": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "BAO:0002162",  # concentration response endpoint -- http://www.bioassayontology.org/bao#BAO_0002162
                "description": "Method used to quantify the strength of the association is IC50",
                "value": "BAO:0000190",  # IC50 -- http://www.bioassayontology.org/bao#BAO_0000190
                "value_type_id": "biolink:id"
        },
        "AUC": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "BAO:0002162",  # concentration response endpoint -- http://www.bioassayontology.org/bao#BAO_0002162
                "description": "Method used to quantify the strength of the association is AUC",
                "value": "BAO:0002120",  # AUC -- http://www.bioassayontology.org/bao#BAO_0002120
                "value_type_id": "biolink:id"
        }
}

correlation_statistic = {
        "T-test": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "NCIT:C53236",  # Correlation Test -- http://purl.obolibrary.org/obo/NCIT_C53236
                "description": "t-test was used to compute the p-value for the association",
                "value": "NCIT:C53231",  # t-Test -- http://purl.obolibrary.org/obo/NCIT_C53231
                "value_type_id": "biolink:id"
        },
        "Spearman_correlation": {
                "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                "attribute_type_id": "NCIT:C53236",  # Correlation Test -- http://purl.obolibrary.org/obo/NCIT_C53236
                "description": "Spearman Correlation Test was used to compute the p-value for the association",
                "value": "NCIT:C53249",  # Spearman Correlation Test -- http://purl.obolibrary.org/obo/NCIT_C53249
                "value_type_id": "biolink:id"
        }
}


class Identifier:
    """
    This class is to split a full CURIE-like ID by colon and reorganize the results into JSON format.
    A full ID can be defined as <FULL-ID> = <PREFIX>:<LOCAL-ID>. The desired JSON format by BTE is like:

        {
            "id" : <FULL-ID>,
            <PREFIX> : <LOCAL-ID>
        }

    However there are some extra rules. (See https://github.com/biothings/pending.api/issues/56 for more).

    1. Some prefixes should be mapped to another form, like "CHEMBL" to "CHEMBL.COMPOUND"
    2. If a prefix is mapped, the prefix part in its corresponding full ID should also be mapped
    3. For certain types of prefixes, its corresponding local ID should always be prefixed, i.e. the local ID should be identical to the full ID
    4. Any prefix should be lowercase, and period (.) within should be replaced with underscore (_). However, this rule does not apply to the prefix part in a full ID.

    E.g. a full ID "CHEBI:90227", according to rule 3 and 4, will be formatted to:

        {
            "id" : "CHEBI:90227",
            "chebi" : "CHEBI:90227"
        }

    E.g. a full ID "CHEMBL:CHEMBL62136", according to rule 1, 2, and 4, will be formatted to:

        {
            "id" : "CHEMBL.COMPOUND:CHEMBL62136",
            "chembl_compound" : "CHEMBL62136"
        }

    Typically when a full ID is not received as <PREFIX>:<LOCAL-ID>, it will be discarded directly, except for gene ID starting with "ENSG0". In such cases, a prefix "ENSEMBL" will precede by default.
    """
    # as defined in https://github.com/biothings/biomedical_id_resolver.js/blob/master/src/config.ts#L4
    ALWAYS_PREFIXED = set(['RHEA', 'GO', 'CHEBI', 'HP', 'MONDO', 'DOID', 'EFO', 'UBERON', 'MP', 'CL', 'MGI'])

    # see Colleen's suggestion in https://github.com/biothings/pending.api/issues/56#issuecomment-1063607497
    # Prefix naming follows the biolink model, as defined in https://github.com/biolink/biolink-model/blob/master/context.jsonld
    PREFIX_MAPPING = {
        "PUBCHEM": "PUBCHEM.COMPOUND",
        "CID": "PUBCHEM.COMPOUND",
        "CHEMBL": "CHEMBL.COMPOUND"
    }

    def __init__(self, _id: str):
        self.full_id = _id
        self.prefix = None
        self.local_id = None

    def parse(self):
        if not self.full_id:
            raise TypeError(f"Cannot parse empty value. Got {self.full_id}.")

        id_parts = self.full_id.split(':')
        num_parts = len(id_parts)
        if num_parts != 2:
            raise ValueError(f"Exactly 2 parts required after splitting on a single colon. Got {num_parts}.", num_parts)

        prefix, local_id = id_parts[0], id_parts[1]
        prefix = self.PREFIX_MAPPING.get(prefix, prefix)

        self.full_id = f"{prefix}:{local_id}"
        self.prefix = prefix.replace(r".", r"_").lower()
        self.local_id = local_id if prefix not in self.ALWAYS_PREFIXED else local_id

    def to_dict(self, full_id_key="id"):
        return {full_id_key: self.full_id, self.prefix: self.local_id}

    @classmethod
    def create_subject_id(cls, _id: str):
        try:
            id_obj = cls(_id)
            id_obj.parse()
        except TypeError:
            return None
        except ValueError as ve:
            num_parts = ve.args[1]
            if num_parts == 1 and _id.startswith('ENSG0'):
                return cls.create_subject_id('ENSEMBL:' + _id)
            else:
                return None

        return id_obj

    @classmethod
    def create_object_id(cls, _id: str):
        try:
            id_obj = Identifier(_id)
            id_obj.parse()
        except (TypeError, ValueError):
            return None

        return id_obj


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
    print(f"INFO: Reading {filename_path}", file=sys.stderr)
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

            # print(line)
            counter += 1

            subject_id = Identifier.create_subject_id(line[1])
            if subject_id is None:
                continue

            # subject = {
            #     "id": subject_id,
            #     "name": line[0],
            #     subject_id_key: subject_id_value,
            #     "type": 'biolink:' + line[4]
            # }
            subject = {
                "name": line[0],
                "type": 'biolink:' + line[4],
                **subject_id.to_dict()
            }

            object_category = line[8]
            if object_category == 'ChemicalSubstance':
                object_category = 'SmallMolecule'

            object_id = Identifier.create_object_id(line[7])
            if object_id is None:
                continue

            # object_ = {
            #     "id": object_id,
            #     "name": line[6],
            #     object_id_key: object_id_value,
            #     "type": 'biolink:' + object_category
            # }
            object_ = {
                "name": line[6],
                "type": 'biolink:' + object_category,
                **object_id.to_dict()
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
                    "attribute_type_id": "EDAM:data_0951",  # statistical estimate score -- http://edamontology.org/data_0951
                    "description": "Confidence metric for the association",
                    "value": float(line[13]),
                    "value_type_id": "EDAM:data_1669",  # P-value -- http://edamontology.org/data_1669
                    "attributes": [attributes]  # sub-attributes should be a list per TRAPI standard
                }
            )

            # sample size
            edge_attributes.append(
                {
                    "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                    "attribute_type_id": "GECKO:0000106",  # sample size - http://purl.obolibrary.org/obo/GECKO_0000106
                    "description": "Sample size used to compute the correlation",
                    "value": int(line[16]),
                }
            )

            # disease context
            edge_attributes.append(
                {
                    "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                    "attribute_type_id": "biolink:has_disease_context",  # I made this up, but similar to biolink:has_population_context
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
                    "attributes": [  # sub-attributes should be a list per TRAPI standard
                        {
                            "attribute_source": "infores:biothings-multiomics-biggim-drugresponse",
                            "attribute_type_id": "biolink:Publication",
                            "description": "Publication describing the dataset used to compute the association",
                            "value": pmid,
                            "value_type_id": "biolink:id"
                        }
                    ]
                }
            )

            association = {
                "edge_label": '_'.join(line[9].split(' ')),
                "edge_attributes": edge_attributes
            }

            # if counter / 10000 == int(counter / 10000):
            #    print(f"{counter}.. ", end='', flush=True)

            # Create a unique record_id, verify that it's unique, and then create a hash to make it shorter
            record_id = 'DRKP-' + '-'.join([subject_id.full_id, line[9], object_id.full_id, line[18], line[13]])
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
    filename_path = os.path.join(data_folder, "Table_DrugResponse_KP_v2021.11.21_rm_redundance_v2022.2.25.csv")
    for row in load_file(filename_path):
        yield row


def main():
    counter = 0
    verbose = True
    for row in load_data('.'):
        if verbose:
            print(json.dumps(row, sort_keys=True, indent=2))
        counter += 1


if __name__ == "__main__":
    main()
