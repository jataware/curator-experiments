# Example 1: Find cases of lymphoblastic leukemia with a JAK1 somatic mutation and save the result to a csv
```
import pandas as pd
from pandas import json_normalize
import requests
import json


def get_ssm_occurrences():
    endpoint = "https://api.gdc.cancer.gov/ssm_occurrences"

    # Define the endpoint and filters
    filters = {
        "op": "and",
        "content": [
            {
                "op": "=",
                "content": {
                    "field": "case.disease_type",
                    "value": "*lymphoblastic leukemia*"
                }
            },
            {
                "op": "in",
                "content": {
                    "field": "ssm.consequence.transcript.gene.symbol",
                    "value": ["JAK1"]
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

    # save as CSV
    ssms.to_csv(f"ssm_occurrences_lymphoblastic_leukemia_JAK1.csv", index=False)



if __name__ == "__main__":
    get_ssm_occurrences()
```

