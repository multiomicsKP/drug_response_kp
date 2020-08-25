import csv
import os
import json
import glob
from biothings_client import get_client
from biothings.utils.dataload import dict_sweep
import requests


DISEASE_NAME_ID_MAPPING = {
    "LAML": "MONDO:0018874",
    "ACC": "MONDO:0008734",
    "BLCA": ["MONDO:0004056", "MONDO:0004163"],
    "LGG": "MONDO:0005499",
    "BRCA": "MONDO:0006256",
    "CESC": ["MONDO:0006143", "MONDO:0000554"],
    "CHOL": "MONDO:0019087",
    "LCML": "MONDO:0011996",
    "COAD": "MONDO:0002271",
    "ESCA": ["MONDO:0003093", "MONDO:0005580"],
    "GBM": "MONDO:0018177",
    "HNSC": "MONDO:0010150",
    "KICH": "MONDO:0017885",
    "KIRC":	"MONDO:0005005",
    "KIRP":	"MONDO:0017884",
    "LIHC":	"MONDO:0007256",
    "LUAD":	"MONDO:0005061",
    "LUSC":	"MONDO:0005097",
    "DLBC":	"MONDO:0018905",
    "MESO":	"MONDO:0005065",
    "OV": "MONDO:0006046",
    "PAAD":	"MONDO:0006047",
    "PCPG":	["MONDO:0004974", "MONDO:0000448"],
    "PRAD": "MONDO:0005082",
    "READ":	"MONDO:0002169",
    "SARC":	"MONDO:0005089",
    "SKCM":	"MONDO:0005012",
    "STAD":	"MONDO:0005036",
    "TGCT":	"MONDO:0010108",
    "THYM":	"MONDO:0006456",
    "THCA":	"MONDO:0015075",
    "UCS": "MONDO:0006485",
    "UCEC": "MONDO:0000553",
    "UVM": "MONDO:0006486",
    "ALL": "MONDO:0004967",
    "MM": "MONDO:0005170",
    "NB": "MONDO:0005072",
    "SCLC": "MONDO:0008433"
}

MYCHEM_CHEMICAL_NAME_FIELDS = [
    "chembl.pref_name",
    "drugbank.name",
    "umls.name",
    "ginas.preferred_name",
    "pharmgkb.name",
    "chebi.name",
    "drugbank.international_brands.name",
    "chembl.molecule_synonyms.synonyms",
    "drugbank.synonyms",
    "drugcentral.synonyms",
    "chebi.synonyms",
]

MYCHEM_CHEMBL_FIELDS = [
    "chembl.molecule_chembl_id",
    "drugbank.xrefs.chembl",
    "drugcentral.xrefs.chembl_id",
]

MYCHEM_PUBCHEM_FIELDS = [
    "pubchem.cid",
    "drugbank.xrefs.pubchem.cid",
    "drugcentral.xrefs.pubchem_cid",
    "pharmgkb.xrefs.pubchem.cid",
]

MYCHEM_CHEBI_FIELDS = [
    "chebi.id",
    "chembl.chebi_par_id",
    "drugbank.xrefs.chebi",
    "drugcentral.xrefs.chebi",
]

DRUG_NAME_TO_ID_MAPPING = {
    "ZG-10": "CHEMBL3393606"
}

GENE_SYMBOL_TO_GENE_ID = {

}

NOT_FOUND = []


def preprocess_drug_name(name):
    name = name.replace(
        " (rescreen)", "").replace(" (50 uM)", "")
    if "," in name:
        name = name.split(',')[0]
    return name


def integrate_manual_mapping(data_folder):
    folder_path = os.path.join(data_folder, "mapping_mannual.csv")
    with open(folder_path) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1].startswith("PUBCHEM:"):
                DRUG_NAME_TO_ID_MAPPING[row[0]] = row[1]


def integrate_lincs(data_folder):
    folder_path = os.path.join(data_folder, "mapping_lincs.csv")
    with open(folder_path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[4] != '':
                DRUG_NAME_TO_ID_MAPPING[row[1]] = 'PUBCHEM:' + str(row[4])


def query_gene_id_by_symbol(symbol):
    if symbol in GENE_SYMBOL_TO_GENE_ID:
        return
    url = 'http://mygene.info/v3/query?q=symbol:{symbol} OR alias:{symbol} OR ensembl.gene:{symbol}&fields=entrezgene&species=human'.replace(
        "{symbol}", symbol)
    res = requests.get(url).json()
    try:
        GENE_SYMBOL_TO_GENE_ID[symbol] = res["hits"][0]["entrezgene"]
    except KeyError:
        GENE_SYMBOL_TO_GENE_ID[symbol] = res["hits"][0]["_id"]
    except IndexError:
        print("{} not mapped to human gene".format(symbol))
        url = 'http://mygene.info/v3/query?q=symbol:{symbol}&fields=entrezgene'.replace(
            "{symbol}", symbol)
        res = requests.get(url).json()
        for item in res["hits"]:
            if "entrezgene" in item:
                GENE_SYMBOL_TO_GENE_ID[symbol] = item["entrezgene"]
                break


def query_drug_id_by_name(name):
    if name in DRUG_NAME_TO_ID_MAPPING:
        return
    base_url = 'http://mychem.info/v1/query?q='
    for _field in MYCHEM_CHEMICAL_NAME_FIELDS:
        base_url += (_field + ':' + str(name) + ' OR ')
    base_url = base_url[:-4] + '&fields=' + ','.join(
        MYCHEM_PUBCHEM_FIELDS + MYCHEM_CHEBI_FIELDS + MYCHEM_CHEMBL_FIELDS + MYCHEM_CHEMICAL_NAME_FIELDS) + '&dotfield=true&size=100'
    res = requests.get(base_url).json()
    if res.get("hits") and len(res['hits']) > 0:
        for rec in res.get("hits"):
            NAME_MATCH = False
            try:
                for field_name in MYCHEM_CHEMICAL_NAME_FIELDS:
                    if rec.get(field_name):
                        if isinstance(rec.get(field_name), list):
                            if name.lower() in [item.lower() for item in rec.get(field_name)]:
                                NAME_MATCH = True
                                continue
                        else:
                            if name.lower() == rec.get(field_name).lower():
                                NAME_MATCH = True
                                break
            except:
                pass
            if not NAME_MATCH:
                continue
            for field_name in MYCHEM_PUBCHEM_FIELDS + MYCHEM_CHEBI_FIELDS + MYCHEM_CHEMBL_FIELDS:
                if field_name in rec:
                    if field_name in MYCHEM_PUBCHEM_FIELDS:
                        DRUG_NAME_TO_ID_MAPPING[name] = "PUBCHEM:" + \
                            str(rec.get(field_name))
                    elif field_name in MYCHEM_CHEMBL_FIELDS:
                        DRUG_NAME_TO_ID_MAPPING[name] = "CHEMBL.COMPOUND:" + \
                            str(rec.get(field_name))
                    else:
                        DRUG_NAME_TO_ID_MAPPING[name] = rec.get(field_name)
                    print("found mapping for {}".format(name))
                    break
            if DRUG_NAME_TO_ID_MAPPING.get(name):
                break
    if not DRUG_NAME_TO_ID_MAPPING.get(name):
        NOT_FOUND.append(name)
        print("drug name {} not found mapping to chembl or chebi".format(name))


def load_file(file_path):
    with open(file_path) as f:
        reader = csv.reader(f, delimiter=',')
        disease_abbr = file_path.split('/')[-1].split('_')[0]
        try:
            mondo = DISEASE_NAME_ID_MAPPING[disease_abbr]
        except KeyError:
            raise Exception(
                "disease abbreviation {} not found in DISEASE_NAME_ID_MAPPING".format(disease_abbr))
        next(reader)
        for row in reader:
            drug_name = preprocess_drug_name(row[4])
            if drug_name not in DRUG_NAME_TO_ID_MAPPING and drug_name not in NOT_FOUND:
                query_drug_id_by_name(drug_name)
            row[1] = row[1].replace('_', '.')
            if row[1] not in GENE_SYMBOL_TO_GENE_ID:
                query_gene_id_by_symbol(row[1])
            if drug_name not in DRUG_NAME_TO_ID_MAPPING:
                drug_id = "name:" + str(drug_name)
            else:
                drug_id = DRUG_NAME_TO_ID_MAPPING[drug_name]
            yield dict_sweep({
                "_id": '-'.join([row[1], str(row[4]), str(row[5]), str(row[11])]),
                "subject": {
                    "id": "NCBIGene:" + str(GENE_SYMBOL_TO_GENE_ID[row[1]]) if GENE_SYMBOL_TO_GENE_ID.get(row[1]) else "SYMBOL:" + row[1],
                    "NCBIGene": GENE_SYMBOL_TO_GENE_ID.get(row[1], 'NA'),
                    "SYMBOL": row[1],
                    "type": "Gene"
                },
                "object": {
                    "id": drug_id,
                    "PUBCHEM": drug_id.split(':')[-1] if drug_id.startswith("PUBCHEM:") else "NA",
                    "CHEMBL.COMPOUND": drug_id.split(':')[-1] if drug_id.startswith("CHEMBL.COMPOUND:") else "NA",
                    "CHEBI": drug_id if drug_id.startswith("CHEBI:") else "NA",
                    "name": drug_name,
                    "type": "ChemicalSubstance"
                },
                "association": {
                    "edge_label": "related_to",
                    "pvalue": float(row[5]),
                    "method": "t-test",
                    "effect_size": float(row[7]),
                    "sample_size": int(row[8]),
                    "size_mut": int(row[9]),
                    "size_wt": int(row[10]),
                    "median_ic50_mut": float(row[11]),
                    "median_ic50_wt": float(row[12]),
                    "ic50s_mut": json.loads(row[13]),
                    "ic50s_wt": json.loads(row[14]),
                    "provided_by": row[16],
                    "publications": "PMC:" + row[17],
                    "context": {
                        "disease": {
                            "id": mondo if isinstance(mondo, str) else mondo[0],
                            "mondo": mondo
                        }
                    }
                }
            }, vals=['NA'])


def load_data(data_folder):
    folder_path = os.path.join(data_folder, "ALL_csvs/*IC50_GDSC.csv")
    integrate_lincs(data_folder)
    integrate_manual_mapping(data_folder)
    for path in glob.glob(folder_path):
        print("===============================================")
        print("processing file {}".format(path))
        for item in load_file(path):
            yield item
