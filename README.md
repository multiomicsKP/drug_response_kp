## Overview:  
Multiomics-biggim-drugresponse KP is developed the Multiomics team supported by the Service Provider (BioThings+SmartAPI) team and the Exploring Agent (BTE) team under the NCATs [Translator](https://github.com/NCATSTranslator) project. The design of the predicates is supported by the Biolink team. It is modeled using the cancer cell line data from GDSC to find the emperial associations between gene mutation, gene expression and drug sensitivity measurements (Area under the curve (AUC) or IC50). 

## Description of the embbeded graphs:
Subject: Gene\
Object: SmallMolecule \
Predicates: [biolink:associated_with_sensitivity_to, biolink:associated_with_sensitivity_to]

## EPC infomation:
Data resource: Genomics of Drug Sensitivity in Cancer (GDSC), Francesco Iorio et al., Cell, 2016 \
P-value: the significance of t-test statistics of the IC50 values between the mutated cell lines and the wild type cell lines. (mutation-based)\
P-value: the significance of Spearman correaltions between the AUC values and the gene expression in cell lines. (Expression-based)\
Effect_size: the difference of IC50 values between the mutated cell lines and the wild type cell lines.\
Correlation_coefficient: Spearman correlation coefficient\
sample_size: the number of samples.
disease_context: disease types (tumor types) for the cell lines.

## Example of queries:
### Example1: which drugs are related to a gene?
<code>curl -X 'POST' \
  'https://api.bte.ncats.io/v1/smartapi/adf20dd6ff23dfe18e8e012bde686e31/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": {
    "query_graph": {
      "edges": {
        "e00": {
          "exclude": false,
          "object": "n01",
          "predicates": [
            "biolink:related_to"
          ],
          "subject": "n00"
        }
      },
      "nodes": {
        "n00": {
          "categories": [
            "biolink:Gene",
            "biolink:Protein"
          ],
          "ids": [
            "NCBIGene:7157"
          ],
          "is_set": false
        },
        "n01": {
          "categories": [
            "biolink:SmallMolecule"
          ],
          "is_set": true
        }
      }
    }
  }
}'
</code>

## Example 2: which drugs are associated with sensitivity to a gene?
<code>curl -X 'POST' \
  'https://api.bte.ncats.io/v1/smartapi/adf20dd6ff23dfe18e8e012bde686e31/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": {
    "query_graph": {
      "edges": {
        "e00": {
          "exclude": false,
          "object": "n01",
          "predicates": [
            "biolink:associated_with_sensitivity_to"
          ],
          "subject": "n00"
        }
      },
      "nodes": {
        "n00": {
          "categories": [
            "biolink:Gene",
            "biolink:Protein"
          ],
          "ids": [
            "NCBIGene:7157"
          ],
          "is_set": false
        },
        "n01": {
          "categories": [
            "biolink:SmallMolecule"
          ],
          "is_set": true
        }
      }
    }
  }
}'
</code>
## Example 3: which drugs are associated with resistance to a gene?
<code>curl -X 'POST' \
  'https://api.bte.ncats.io/v1/smartapi/adf20dd6ff23dfe18e8e012bde686e31/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": {
    "query_graph": {
      "edges": {
        "e00": {
          "exclude": false,
          "object": "n01",
          "predicates": [
            "biolink:associated_with_resistance_to"
          ],
          "subject": "n00"
        }
      },
      "nodes": {
        "n00": {
          "categories": [
            "biolink:Gene",
            "biolink:Protein"
          ],
          "ids": [
            "NCBIGene:7157"
          ],
          "is_set": false
        },
        "n01": {
          "categories": [
            "biolink:SmallMolecule"
          ],
          "is_set": true
        }
      }
    }
  }
}'

</code>