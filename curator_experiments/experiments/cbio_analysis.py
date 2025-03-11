from pathlib import Path
from functools import cache
from .analysis_utils import Score, Analyzer

import pdb

here = Path(__file__).parent
workdir, task_variant = here / '../../workdir_20250225_132405', '(GDC w/ No Examples)'                 # step 2: no examples



def main():
    plot_results()


@cache
def get_cbio_reference():
    pdb.set_trace()
    # # load the reference solution
    # reference_path = here / 'ssm_occurrences_lymphoblastic_leukemia_JAK1.csv'
    # reference = pd.read_csv(reference_path)
    # solution_ids = set(reference['id'].tolist())  # IDs in the CSV were are looking for to indicate if a trial is correct
    # # solution_num_ids = len(solution_ids)

    # return reference, solution_ids




def evaluate_cbio_trial(trial_name: str, code_chunks: list[str]) -> Score:
    reference, solution_ids = get_cbio_reference()

    data_path = workdir/f'{trial_name}.csv'
        
    # see if a file was even created
    if not data_path.exists():
        return Score(False)
    
    # TODO
    pdb.set_trace()
        
    # # see if the file is empty
    # try:
    #     data = pd.read_csv(data_path)
    # except (pd.errors.EmptyDataError, Exception):
    #     return GDCScore(False, 0, False, False, True)
        
    # # see if csv has correct number of rows or any data at all
    # correct_num_rows = len(data) == len(reference)
    # any_data = len(data) > 0
    
    # # check how many ids are correct
    # try:
    #     trial_ids = set(data['id'].tolist())
    # except KeyError:
    #     # no id column, so just check the raw text from the file
    #     raw_text = data_path.read_text()
    #     trial_ids = set([id for id in solution_ids if id in raw_text])

    # # see if the ids are correct. (jaccard score i.e. IoU)
    # correct_ids = len(solution_ids.intersection(trial_ids)) / len(solution_ids.union(trial_ids))

    # # full solution correctness is if correct_ids == 1 (i.e. 8/8)
    # success = correct_ids == 1

    # # save the score
    # return GDCScore(success, correct_ids, correct_num_rows, any_data, True)



if __name__ == '__main__':
    main()