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
                "ENSEMBL": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "type": {
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
                "CHEBI": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "type": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "CHEMBL.COMPOUND": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "PUBCHEM": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "HMS_LINCS_ID": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "CID": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                }
            }
        }
    }
