from pathlib import Path
from functools import cache
import pandas as pd
from dataclasses import dataclass
from .analysis_utils import Score, Analyzer

import pdb

here = Path(__file__).parent
# workdir, task_variant = here / '../../workdir_20250311_125333', '(CBioportal w/ No Examples)'
workdir, task_variant = here / '../../workdir_20250312_102201', '(CBioportal w/ Reference Example)'

@dataclass
class CBioScore(Score):
    correct_ids_score: float

def main():
    analyzer = Analyzer(
        workdir=workdir,
        task_variant=task_variant,
        evaluate_trial_fn=evaluate_cbio_trial,
        reference_code=get_cbio_reference_code()
    )
    analyzer.plot_results()


@cache
def get_cbio_reference():
    # load the reference solution
    reference_path = here / 'stat5_all_studies.csv'
    reference = pd.read_csv(reference_path)
    solution_ids = set(reference['sample_id'].tolist())  # IDs in the CSV were are looking for to indicate if a trial is correct

    return reference, solution_ids


def get_cbio_reference_code() -> str:
        """Return a stripped version of the reference solution"""
        return (here / 'cbio_reference_solution.py').read_text()


def evaluate_cbio_trial(trial_name: str, code_chunks: list[str], pass_threshold=0.95) -> CBioScore:
    reference, solution_ids = get_cbio_reference()

    data_path = workdir/f'{trial_name}.csv'
        
    # see if a file was even created
    if not data_path.exists():
        return CBioScore(False, 0)
            
    # see if the file is empty
    try:
        data = pd.read_csv(data_path)
    except (pd.errors.EmptyDataError, Exception):
        return CBioScore(False, 0)
        
    
    # check how many ids are correct
    try:
        candidate_columns = {'sample_id', 'SampleID', 'sampleId', 'Sample ID'}
        column_name = set(data.columns).intersection(candidate_columns)
        if len(column_name) == 0:
            return CBioScore(False, 0)
        if len(column_name) > 1:
            print(f"Warning: Multiple candidate columns found: {column_name}. Using the first one.")
        column_name = column_name.pop()
        trial_ids = set(data[column_name].tolist())
    except KeyError:
        # search for the best matching column
        best_column = None
        best_match_count = 0
        for column in data.columns:
            match_count = sum(1 for id in solution_ids if id in data[column].astype(str).tolist())
            if match_count > best_match_count:
                best_match_count = match_count
                best_column = column
        if best_column is not None:
            trial_ids = set(data[best_column].astype(str).tolist())
        else:
            trial_ids = set()

    # see if the ids are correct. (jaccard score i.e. IoU)
    correct_ids_score = len(solution_ids.intersection(trial_ids)) / len(solution_ids.union(trial_ids))

    # full solution correctness is if correct_ids == 1 (i.e. 8/8)
    success = correct_ids_score > pass_threshold

    # # save the score
    return CBioScore(success, correct_ids_score)



if __name__ == '__main__':
    main()