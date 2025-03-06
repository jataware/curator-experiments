## Example 1: Query the GDC for cases of myeloid leukemia with a JAK2 somatic mutation and return the results as a pandas dataframe.

```
import pandas as pd
from pandas import json_normalize

import requests
import json

# Define the endpoint and filters
endpoint = "https://api.gdc.cancer.gov/ssm_occurrences"
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
```

## Example 2: Get all cases where disease type is myeloid leukemia from GDC and return the results as a pandas dataframe. Paginate through the results to fetch all available cases

```
import pandas as pd
from pandas import json_normalize

import requests
import json

# Define the endpoint and filters
endpoint = "https://api.gdc.cancer.gov/cases"
filters = {
    "op": "=",
    "content": {
        "field": "disease_type",
        "value": "*myeloid leukemia*"
    }
}

# Define the fields to be returned
fields = [
    "submitter_id",
    "case_id",
    "primary_site",
    "disease_type",
    "diagnoses.age_at_diagnosis",
    "diagnoses.primary_diagnosis",
    "demographic.gender",
    "exposures.tobacco_smoking_status",
    "files.file_id",
    "files.file_name",
    "files.data_type",
    "files.experimental_strategy"
]

# Initialize pagination variables
all_cases = []
current_page = 1
page_size = 1000

while True:
    # Construct the request parameters
    params = {
        "filters": json.dumps(filters),
        "fields": ",".join(fields),
        "format": "JSON",
        "size": page_size,
        "from": (current_page - 1) * page_size
    }

    # Send the request
    response = requests.get(endpoint, params=params)

    # Check for successful response
    if response.status_code == 200:
        data = response.json()
        cases = data["data"]["hits"]
        all_cases.extend(cases)
        if len(cases) < page_size:
            break
        current_page += 1
    else:
        print(f"Error: {response.status_code} - {response.text}")
        break

# Convert the results to a DataFrame
cases_df = pd.DataFrame(json_normalize(all_cases))
print(f"There are {len(cases_df)} cases in GDC for AML")
# Display the DataFrame
cases_df.head()
```

## Example 3: Get all cases from GDC with no filters. Fetch only the case ids and paginate through the results to fetch all available cases. Store the results as a dataframe

```
import requests
import json
import pandas as pd
from pandas import json_normalize

# Define the fields to be returned
fields = [
    "case_id",
]

# Initialize pagination variables
all_cases = []
current_page = 1
page_size = 1000

while True:
    # Construct the request parameters
    params = {
        "fields": ",".join(fields),
        "format": "JSON",
        "size": page_size,
        "from": (current_page - 1) * page_size
    }

    # Send the request
    response = requests.get(endpoint, params=params)

    # Check for successful response
    if response.status_code == 200:
        data = response.json()
        cases = data["data"]["hits"]
        all_cases.extend(cases)
        if len(cases) < page_size:
            break
        current_page += 1
    else:
        print(f"Error: {response.status_code} - {response.text}")
        break

# Convert the results to a DataFrame
all_cases_df = pd.DataFrame(json_normalize(all_cases))
print(f"There are {len(all_cases_df)} cases in GDC in total")
# Display the DataFrame
all_cases_df.head()
```

## Example 4: Get simple somatic mutation occurrences (cases) from GDC where the primary site is bronchus and lung, the gender is male, the age at diagnosis is less than 45 years old, and the patient is a lifelong non-smoker. Return the results as a pandas dataframe.

```
import pandas as pd
from pandas import json_normalize

import requests
import json

# Define the endpoint and filters
endpoint = "https://api.gdc.cancer.gov/ssm_occurrences"
filters = {
    "op": "and",
    "content": [
        {
            "op": "in",
            "content": {
                "field": "case.primary_site",
                "value": ["Bronchus and lung"]
            }
        },
        {
            "op": "in",
            "content": {
                "field": "case.demographic.gender",
                "value": ["male"]
            }
        },
        {
            "op": "<",
            "content": {
                "field": "case.diagnoses.age_at_diagnosis",
                "value": 16436 # 45 years in days
            }
        },
        {
            "op": "in",
            "content": {
                "field": "case.exposures.tobacco_smoking_status",
                "value": ["Lifelong Non-smoker"]
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
    "case.diagnoses.primary_diagnosis",
    "case.primary_site",
    "case.demographic.gender",
    "case.diagnoses.age_at_diagnosis",
    "case.exposures.tobacco_smoking_status"
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

# Check for successful response
if response.status_code == 200:
    data = response.json()
    # Extract and display the mutation data
    mutations = data["data"]["hits"]
    print(f"Found {len(mutations)} mutations in lung cancer cases for males under 45 who never smoked:")
    lung_mutation_df = pd.DataFrame(json_normalize(mutations))
else:
    print(f"Error: {response.status_code} - {response.text}")
  
lung_mutation_df.head()
```


## Example 5: In GDC find all cases of myeloid leukemia with a JAK2 somatic mutation and save the result to a csv named trial_12.csv

```
import requests
import json
import pandas as pd

# This is the endpoint for searching for somatic mutations.
endpt = "https://api.gdc.cancer.gov/ssm_occurrences"

# Filters to find myeloid leukemia cases with JAK2 mutations
filters = {
    "op": "and",
    "content": [
        {
            "op": "in",
            "content": {
                "field": "case.disease_type", 
                "value": [
                    "Acute myeloid Leukemia",
                    "myeloid Leukemia"
                ]
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

# This is the list of fields that will be returned.
fields = [
    "case.submitter_id",
    "case.disease_type",
    "ssm.consequence.transcript.gene.symbol"
]

# These are the parameters that will be passed to the API.
params = {
    "filters": json.dumps(filters),
    "fields": ",".join(fields),
    "format": "JSON",
    "size": "1000"
}

# Send a GET request to the API and convert the result to a JSON object.
response = requests.get(endpt, params=params)
data = response.json()

# Create a pandas DataFrame from the returned data
df = pd.DataFrame(data["data"]["hits"])

# Save DataFrame to a CSV file
df.to_csv("trial_12.csv", index=False)
```


## Example 6: In GDC find all cases of myeloid leukemia with a JAK2 somatic mutation and save the result to a csv named trial_24.csv

```
import requests
import json
import pandas as pd

# This is the endpoint we will use
endpoint = 'https://api.gdc.cancer.gov/ssm_occurrences'

# Create the filter
filters = {
    "op": "and",
    "content":[
        {
            "op": "in",
            "content":{
                "field": "case.disease_type",
                "value": [
                    "*myeloid leukemia*"
                    ]
            }
        },
        {
            "op":"=",
            "content":{
                "field":"ssm.consequence.transcript.gene.symbol",
                "value":"JAK2"
            }
        }
    ]
}

# These are the fields we want to get back
fields = [
    "case.submitter_id",
    "case.disease_type",
    "ssm.consequence.transcript.gene.symbol"
]

# The format of the response
format = 'JSON'

# How big should the response be
size = 100

# Construct the payload
params = {
    'filters': json.dumps(filters),
    'fields': ','.join(fields),
    'format': format,
    'size': size
}

# Get the response from the API
response = requests.get(endpoint, params = params)

# Transform the response into a pandas dataframe
df = pd.json_normalize(response.json()['data']['hits'])

# Save the dataframe to a file
df.to_csv('trial_24.csv', index=False)

```




## Example 7: In GDC find all cases of myeloid leukemia with a JAK2 somatic mutation and save the result to a csv named trial_34.csv
```
import requests
import json
import pandas as pd

# This is the endpoint we will use
endpoint = 'https://api.gdc.cancer.gov/ssm_occurrences'

# Create a filter to find the cases we want
filters = {
    "op": "and",
    "content":[
        {
            "op": "=",
            "content":{
                "field": "ssm.consequence.transcript.gene.symbol",
                "value": "JAK2"
            }
        },
        {
            "op": "=",
            "content":{
                "field": "case.disease_type",
                "value": "*myeloid leukemia"
            }
        }
    ]
}

# These are the fields we will include in the output
fields = [
    "case.case_id",
    "case.disease_type",
    "ssm.consequence.transcript.gene.symbol"
]

# The format of the output
format = 'JSON'

# The size of the output.
size = 100

# Construct the parameters for the query
params = {
    'filters': json.dumps(filters),
    'fields': ','.join(fields),
    'format': format,
    'size': size
}

# Send a GET request to the API
response = requests.get(endpoint, params = params)

# Load the response into a pandas dataframe
df = pd.json_normalize(response.json()['data']['hits'])

# Save the dataframe to a CSV file
df.to_csv('trial_34.csv', index=False)

```



## Example 8: In GDC find all cases of myeloid leukemia with a JAK2 somatic mutation and save the result to a csv named trial_58.csv

```
import requests
import json
import pandas as pd

fields = [
    "case.case_id",
    "case.disease_type",
    "case.primary_site",
    "ssm.consequence.transcript.gene.symbol",
]

filters = {
    "op": "and",
    "content": [
        {
            "op": "in",
            "content": {
                "field": "case.disease_type",
                "value": [
                    "Acute Myeloid Leukemia",
                    "Myeloid Leukemia",
                ]
            }
        },
        {
            "op": "=",
            "content": {
                "field": "ssm.consequence.transcript.gene.symbol",
                "value": "JAK2"
            }
        }
    ]
}

params = {
    "filters": json.dumps(filters),
    "fields": ",".join(fields),
    "format": "JSON",
    "size": "10000"
}

response = requests.get("https://api.gdc.cancer.gov/ssm_occurrences", params = params)

if response.status_code == 200:
    df = pd.DataFrame(response.json()["data"]["hits"])
    df.to_csv("trial_58.csv", index=False)
else:
    print("Failed to retrieve data: ", response.status_code)

```