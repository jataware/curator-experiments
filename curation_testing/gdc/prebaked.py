import pandas as pd
from pandas import json_normalize

import requests
import json



from dataclasses import dataclass

@dataclass
class Content:
    field: str  #TODO: this needs to be pulled from facets...
    value: str  #TODO: this needs to be pulled from facets...


import pdb


def get_ssm_occurrences():
    endpoint = "https://api.gdc.cancer.gov/ssm_occurrences"
    pdb.set_trace()


# Define the endpoint and filters
filters = {
    "op": "and",
    "content": [
        {
            "op": "=",
            "content": {
                "field": "case.disease_type",
                "value": "*myeloid leukemia*"
            }
        },
        {
            "op": "in",
            "content": {
                "field": "ssm.consequence.transcript.gene.symbol",
                "value": ["JAK2"]
            }
        }
    ]
}

# Define the fields to be returned
fields = [
    "ssm_id",
    "ssm.consequence.transcript.gene.symbol",
    "ssm.mutation_type",
    "ssm.genomic_dna_change",
    "ssm.consequence.transcript.aa_change",
    "ssm.consequence.transcript.consequence_type",
    "case.project.project_id",
    "case.submitter_id",
    "case.case_id",
    "case.diagnoses.primary_diagnosis"
]

# Construct the request parameters
params = {
    "filters": json.dumps(filters),
    "fields": ",".join(fields),
    "format": "JSON",
    "size": "1000"
}

# Send the request
response = requests.get(endpoint, params=params)
print(f"total hits: {response.json()['data']['pagination']['total']}")
all_ssms = response.json()['data']['hits']

ssms = pd.DataFrame(json_normalize(all_ssms))
ssms.head()