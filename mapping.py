def custom_mapping(cls):
    """
    Method to provide custom mapping to parser. 
    
    Configuration of this method in manifest.json should be: 
    
        "uploader" : { 
            "mapping" : "mapping:custom_mapping"
        }
        
    This is a class method but @classmethod decorator is not necessary. 
    See https://docs.biothings.io/en/latest/tutorial/studio_guide.html#manifest-based-data-plugins
    """
    return {
        "subject": {
            "properties": {
                "id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "name": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "type": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "ensembl": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                }
            }
        },
        "association": {
            "properties": {
                "edge_label": {
                    "type": "text"
                }
            }
        },
        "object": {
            "properties": {
                "id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "name": {
                    "type": "text"
                },
                "type": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "chebi": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "chembl_compound": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "pubchem_compound": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "hms_lincs_id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                }
            }
        }
    }
