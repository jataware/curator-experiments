import requests
import pandas as pd
import time

# Configuration
BASE_URL = "https://www.cbioportal.org/api"

# Define studies and their RNA-seq profiles
STUDY_PROFILES = {
    'aml_target_gdc': {
        'name': 'TARGET-AML (GDC)',
        'profile': 'aml_target_gdc_mrna_seq_tpm_Zscores',
        'type': 'TPM'
    },
    'aml_ohsu_2022': {
        'name': 'OHSU AML 2022',
        'profile': 'aml_ohsu_2022_mrna_median_Zscores',
        'type': 'RPKM'
    }
    # ... other studies ...
}

# Define STAT5 genes with their Entrez IDs
STAT5_GENES = {
    6776: 'STAT5A',
    6777: 'STAT5B'
}

# Function to get RNA-seq samples for a study
def get_rna_seq_samples(study_id):
    """Get list of sample IDs that have RNA-seq data for a study."""
    url = f"{BASE_URL}/studies/{study_id}/sample-lists"
    response = requests.get(url)
    if response.status_code == 200:
        sample_lists = response.json()
        # Find RNA-seq sample list
        rna_list = next((sl['sampleListId'] for sl in sample_lists 
                        if sl['category'] == 'all_cases_with_mrna_rnaseq_data'), None)
        if rna_list:
            # Get sample IDs from the list
            url = f"{BASE_URL}/sample-lists/{rna_list}/sample-ids"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
    return None

# Function to get expression data
def get_expression_data(profile_id, gene_ids, sample_ids):
    """Fetch expression z-scores for specific genes and samples."""
    url = f"{BASE_URL}/molecular-profiles/{profile_id}/molecular-data/fetch"
    # IMPORTANT: Must provide sample IDs explicitly
    data = {
        "sampleIds": sample_ids,  # List of specific sample IDs
        "entrezGeneIds": gene_ids  # List of Entrez gene IDs
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    return None

# Process each study
all_study_data = []

for study_id, study_info in STUDY_PROFILES.items():
    print(f"\nProcessing {study_info['name']}...")
    
    # First get the sample IDs for the study
    sample_ids = get_rna_seq_samples(study_id)
    
    if sample_ids:
        print(f"Found {len(sample_ids)} RNA-seq samples")
        
        # Process samples in chunks to avoid large requests
        chunk_size = 100
        study_data = []
        
        for i in range(0, len(sample_ids), chunk_size):
            chunk = sample_ids[i:i + chunk_size]
            print(f"Fetching data for samples {i+1}-{i+len(chunk)}...")
            
            # Get expression data for this chunk of samples
            expression_data = get_expression_data(
                study_info['profile'], 
                list(STAT5_GENES.keys()), 
                chunk
            )
            
            if expression_data:
                study_data.extend(expression_data)
            time.sleep(0.2)  # Small delay between requests
        
        if study_data:
            # Convert to DataFrame
            df = pd.DataFrame(study_data)
            
            # Add metadata
            df['gene_symbol'] = df['entrezGeneId'].map(STAT5_GENES)
            df['study_id'] = study_id
            df['study_name'] = study_info['name']
            df['measurement_type'] = study_info['type']
            
            # Select and rename columns
            df = df[[
                'study_id', 'study_name', 'measurement_type',
                'gene_symbol', 'sampleId', 'value'
            ]]
            df.columns = [
                'study_id', 'study_name', 'measurement_type',
                'gene', 'sample_id', 'zscore'
            ]
            
            all_study_data.append(df)

# Combine all data
if all_study_data:
    # Create long format
    combined_df = pd.concat(all_study_data, ignore_index=True)
    
    # Create wide format (samples as rows, genes as columns)
    combined_wide = combined_df.pivot_table(
        index=['study_id', 'study_name', 'measurement_type', 'sample_id'],
        columns='gene',
        values='zscore'
    ).reset_index()
    
    # Save both versions
    stat5_all_studies = combined_df  # Long format
    stat5_all_studies_wide = combined_wide  # Wide format



# Save All the data to CSV
stat5_all_studies.to_csv('stat5_all_studies.csv', index=False)
stat5_all_studies_wide.to_csv('stat5_all_studies_wide.csv', index=False)