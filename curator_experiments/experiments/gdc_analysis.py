from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from functools import cache
from .analysis_utils import Score, Analyzer




@dataclass
class GDCScore(Score):
    correct_ids: float
    correct_num_rows: bool
    any_data: bool
    created_file: bool
    # code_match: float #TODO: future will have an agent compare the code



here = Path(__file__).parent
workdir, task_variant = here / '../../workdir_20250225_132405', '(GDC w/ No Examples)'                 # step 2: no examples
# workdir, task_variant = here / '../../workdir_20250228_134952', '(GDC w/ Verbatim Solution Example)'   # step 3a: single verbatim example
# workdir, task_variant = here / '../../workdir_20250303_134057', '(GDC w/ Single Similar Example)'      # step 3b: single similar example
# workdir, task_variant = here / '../../workdir_20250306_121135', '(GDC w/ Verbatim Solution + Examples)'  # step 3c1: multiple examples
# workdir, task_variant = here / '../../workdir_20250305_085435', '(GDC w/ Multiple Examples)'            # step 3c2: multiple examples
# workdir, task_variant = here / '../../workdir_20250305_120842', '(GDC w/ Too Many Examples)'            # step 3d: too many examples

def main():
    analyzer = Analyzer(
        workdir=workdir,
        task_variant=task_variant,
        evaluate_trial_fn=evaluate_gdc_trial,
        reference_code=get_gdc_reference_code()
    )
    analyzer.plot_results()


@cache
def get_gdc_reference() -> tuple[pd.DataFrame, set]:
    # load the reference solution
    reference_path = here / 'ssm_occurrences_lymphoblastic_leukemia_JAK1.csv'
    reference = pd.read_csv(reference_path)
    solution_ids = set(reference['id'].tolist())  # IDs in the CSV were are looking for to indicate if a trial is correct
    # solution_num_ids = len(solution_ids)

    return reference, solution_ids

def get_gdc_reference_code() -> str:
        """Return a stripped version of the reference solution"""
        reference_code_path = here / 'gdc_reference_solution.py'
        reference_code = reference_code_path.read_text()
        reference_code = reference_code.split('"""')[-1].strip()  # remove the docstring

        return reference_code


def evaluate_gdc_trial(trial_name: str, code_chunks: list[str]) -> GDCScore:
    reference, solution_ids = get_gdc_reference()

    data_path = workdir/f'{trial_name}.csv'
        
    # see if a file was even created
    if not data_path.exists():
        return GDCScore(False, 0, False, False, False)
        
    # see if the file is empty
    try:
        data = pd.read_csv(data_path)
    except (pd.errors.EmptyDataError, Exception):
        return GDCScore(False, 0, False, False, True)
        
    # see if csv has correct number of rows or any data at all
    correct_num_rows = len(data) == len(reference)
    any_data = len(data) > 0
    
    # check how many ids are correct
    try:
        trial_ids = set(data['id'].tolist())
    except KeyError:
        # no id column, so just check the raw text from the file
        raw_text = data_path.read_text()
        trial_ids = set([id for id in solution_ids if id in raw_text])

    # see if the ids are correct. (jaccard score i.e. IoU)
    correct_ids = len(solution_ids.intersection(trial_ids)) / len(solution_ids.union(trial_ids))

    # full solution correctness is if correct_ids == 1 (i.e. 8/8)
    success = correct_ids == 1

    # save the score
    return GDCScore(success, correct_ids, correct_num_rows, any_data, True)




    



if __name__ == '__main__':
    main()