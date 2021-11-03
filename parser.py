import os
import csv
import glob

DISEASE_LABEL_MONDO_MAP = {
    "ACC": {"id": "MONDO:0008734", "name": "Adrenocortical carcinoma"},
    "ALL": {"id": "MONDO:0004967", "name": "Acute lymphoblastic leukemia"},
    "BLCA": {"id": ["MONDO:0004056", "MONDO:0004163"], "name": "Bladder Urothelial Carcinoma"},
    "BRCA": {"id": "MONDO:0006256", "name": "Breast invasive carcinoma"},
    "CESC": {"id": ["MONDO:0006143", "MONDO:0000554"], "name": "Cervical squamous cell carcinoma"},
    "CHOL": {"id": "MONDO:0019087", "name": "Cholangiocarcinoma"},
    "COAD": {"id": "MONDO:0002271", "name": "Colon adenocarcinoma"},
    "COAD_READ": {"id": ["MONDO:0002271", "MONDO:0002169"], "name": "Colon/Rectum adenocarcinoma"},
    "DLBC": {"id": "MONDO:0018905", "name": "Lymphoid Neoplasm Diffuse Large B-cell Lymphoma"},
    "ESCA": {"id": ["MONDO:0003093", "MONDO:0005580"], "name": "Esophageal carcinoma"},
    "GBM": {"id": "MONDO:0018177", "name": "Glioblastoma multiforme"},
    "HNSC": {"id": "MONDO:0010150", "name": "Head and Neck squamous cell carcinoma"},
    "KICH": {"id": "MONDO:0017885", "name": "Kidney Chromophobe"},
    "KIRC": {"id": "MONDO:0005005", "name": "Kidney renal clear cell carcinoma"},
    "KIRP": {"id": "MONDO:0017884", "name": "Kidney renal papillary cell carcinoma"},
    "LAML": {"id": "MONDO:0018874", "name": "Acute Myeloid Leukemia"},
    "LCML": {"id": "MONDO:0011996", "name": "Chronic Myelogenous Leukemia"},
    "LGG": {"id": "MONDO:0005499", "name": "Brain Lower Grade Glioma"},
    "LIHC": {"id": "MONDO:0007256", "name": "Liver hepatocellular carcinoma"},
    "LUAD": {"id": "MONDO:0005061", "name": "Lung adenocarcinoma"},
    "LUSC": {"id": "MONDO:0005097", "name": "Lung squamous cell carcinoma"},
    "MESO": {"id": "MONDO:0005065", "name": "Mesothelioma"},
    "MM": {"id": "MONDO:0009693", "name": "Multiple myeloma"},
    "NB": {"id": "MONDO:0005072", "name": "Neuroblastoma"},
    "OV": {"id": "MONDO:0006046", "name": "Ovarian serous cystadenocarcinoma"},
    "PAAD": {"id": "MONDO:0006047", "name": "Pancreatic adenocarcinoma"},
    "PCPG": {"id": ["MONDO:0004974", "MONDO:0000448"], "name": "Pheochromocytoma and Paraganglioma"},
    "PRAD": {"id": "MONDO:0005082", "name": "Prostate adenocarcinoma"},
    "READ": {"id": "MONDO:0002169", "name": "Rectum adenocarcinoma"},
    "SARC": {"id": "MONDO:0005089", "name": "Sarcoma"},
    "SCLC": {"id": "MONDO:0008433", "name": "Small cell lung carcinoma"},
    "SKCM": {"id": "MONDO:0005012", "name": "Skin Cutaneous Melanoma"},
    "STAD": {"id": "MONDO:0005036", "name": "Stomach adenocarcinoma"},
    "TGCT": {"id": "MONDO:0010108", "name": "Testicular Germ Cell Tumors"},
    "THCA": {"id": "MONDO:0015075", "name": "Thyroid carcinoma"},
    "THYM": {"id": "MONDO:0006456", "name": "Thymoma"},
    "UCEC": {"id": "MONDO:0000553", "name": "Uterine Corpus Endometrial Carcinoma"},
    "UCS": {"id": "MONDO:0006485", "name": "Uterine Carcinosarcoma"},
    "UVM": {"id": "MONDO:0006486", "name": "Uveal Melanoma"}
}

NODE_NAME_ID_MAPPING = {}
NODE_NAME_TYPE_MAPPING = {}


def load_nodes_data(data_folder):
    folder_path = os.path.join(data_folder, 'drug_response_gene_expression_nodes.csv')
    with open(folder_path) as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for line in reader:
            NODE_NAME_ID_MAPPING[line[1]] = line[0]
            NODE_NAME_TYPE_MAPPING[line[1]] = line[2]


def load_file(file_path):
    with open(file_path) as f:
        # Load file and get disease abbreviation from file name
        reader = csv.reader(f, delimiter=',')
        disease_abbr = file_path.split('/')[-1].split('.')[-2]

        # Raise exception if disease abbreviation not found in mapping
        disease_info = DISEASE_LABEL_MONDO_MAP.get(disease_abbr, None)
        if disease_info is None:
            raise Exception("Disease abbreviation '{} not found in disease mapping!".format(disease_abbr))

        # Skip header line in file
        next(reader)

        # Get edge data
        for line in reader:
            # Get node 1 information
            node1_name = line[1]
            node1_id = NODE_NAME_ID_MAPPING.get(node1_name, None)
            node1_type = NODE_NAME_TYPE_MAPPING.get(node1_name, None)

            # Get node 2 information
            node2_name = line[2]
            node2_id = NODE_NAME_ID_MAPPING.get(node2_name, None)
            node2_type = NODE_NAME_TYPE_MAPPING.get(node2_name, None)

            # Skip this edge if node mappings do not exist
            if not(all([node1_id, node1_type, node2_id, node2_type])):
                current_nodes = [node1_name, node2_name]
                print("Missing 1 or more node IDs/types for edge {0}-{1}! Skipping this edge.".format(*current_nodes))
                continue

            # Specify properties for subject
            subject = {
                "id": node1_id,
                node1_id.split(':')[0]: node1_id,
                "name": node1_name,
                "type": node1_type
            }

            # Specify properties for object
            object_ = {
                "id": node2_id,
                node2_id.split(':')[0]: node2_id,
                "name": node2_name,
                "type": node2_type
            }

            # Specify properties for predicate
            predicate = {
                "type": "biolink:correlated_with",
                "relation": "RO:0002610",
                "category": "biolink:Association",
                "provided_by": "Big GIM II: Drug response (Multiomics Provider)",
                "provenance": "https://github.com/NCATSTranslator/Translator-All/wiki/Big-GIM-II:-Drug-Response-KP",
                "N": int(line[5]),
                "correlation": float(line[3]),
                "pvalue": float(line[4]),
                "context": {"disease": {"id": disease_info['id'], "name": disease_info['name']}}
            }

            # Yield subject, predicate, and object properties
            yield {
                "_id": '-'.join([line[1], line[2], line[3], line[4], line[5], line[6]]),
                "subject": subject,
                "predicate": predicate,
                "object": object_
            }


def load_data(data_folder):
    # Load nodes data
    load_nodes_data(data_folder)

    # Load edge data from individual files
    folder_path = os.path.join(data_folder, "RMA_proc_basalExp_AUC*")
    for path in glob.glob(folder_path):
        print("===============================================")
        print("processing file {}".format(path))
        for item in load_file(path):
            yield item
