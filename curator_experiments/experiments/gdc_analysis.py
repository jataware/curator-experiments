import yaml
# import json
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
# from adhoc_api.uaii import ClaudeAgent, OpenAIAgent
# from collections import defaultdict
# from time import sleep
from functools import cache
# from .utils import timeout
from .analysis_utils import Score, Analyzer

import pdb



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
    plot_results()


@cache
def get_gdc_reference():
    # load the reference solution
    reference_path = here / 'ssm_occurrences_lymphoblastic_leukemia_JAK1.csv'
    reference = pd.read_csv(reference_path)
    solution_ids = set(reference['id'].tolist())  # IDs in the CSV were are looking for to indicate if a trial is correct
    # solution_num_ids = len(solution_ids)

    return reference, solution_ids



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


# def analyze_trials():
# def identify_solutions() -> tuple[dict[str, list[str]], dict[str, Score], list[str]]:

#     # load all the trials
#     code_path = workdir/'captured_code.yaml'
#     trials: dict = yaml.safe_load(code_path.open())
#     # replace any NoneTypes with []
#     trials: dict[str, list[str]] = {k: v if v is not None else [] for k, v in trials.items()}

#     # save the score of each trial
#     scores: dict[str, Score] = {}

#     # save a list of the trials that are correct
#     successful_trials: list[str] = []

#     # compare each of the trials to the reference
#     for trial, code_chunks in tqdm(trials.items(), desc='Analyzing trials', total=len(trials)):
#         score = evaluate_gdc_trial(trial, code_chunks)
#         scores[trial] = score
#         if score.success:
#             successful_trials.append(trial)
        
#     return trials, scores, successful_trials


def plot_results():
    analyzer = Analyzer(workdir=workdir, task_variant=task_variant)

    trials, scores, successful_trials = analyzer.identify_solutions(evaluate_gdc_trial)
    successful_trial_names = set(successful_trials) # for easy lookup

    # print out a map from each result to the frequency of the result
    # correct_id_counts = [int(score.correct_ids * solution_num_ids) for score in scores.values()]
    # correct_id_scores = set(correct_id_counts)
    # correct_id_freqs = {score: correct_id_counts.count(score) for score in correct_id_scores}
    # print(f"Correct ID Frequencies: {correct_id_freqs}")
    
    # # plot a histogram of the id match %
    # plt.hist(correct_id_counts, bins=range(0, 10), align='left', rwidth=0.8)
    # plt.xticks(range(0, 9))
    # plt.xlabel(f'Number of Correct IDs (max {len(solution_ids)})')
    # plt.ylabel('Number of Trials')
    # plt.title(f'Frequency of Correct Results {task_variant}')
    # plt.savefig(workdir/'correct_ids_histogram.png')
    # plt.show()

    # # plot a histogram of the number of rows
    # num_rows = ['correct' if score.correct_num_rows else 'incorrect' for score in scores.values()]
    # plt.hist(num_rows, bins=range(0, 3), align='left', rwidth=0.8)
    # plt.xlabel('Number of Rows in Result')
    # plt.ylabel('Number of Trials')
    # plt.title(f'Frequency of Correct Number of Rows {task_variant}')
    # plt.savefig(workdir/'num_rows_histogram.png')
    # plt.show()

    # # plot a histogram of the any data
    # any_data = ['yes' if score.any_data else 'no' for score in scores.values()]
    # plt.hist(any_data, bins=range(0, 3), align='left', rwidth=0.8)
    # plt.xlabel('Any Data in Result')
    # plt.ylabel('Number of Trials')
    # plt.title(f'Frequency of Any Data in Result {task_variant}')
    # plt.savefig(workdir/'any_data_histogram.png')
    # plt.show()

    # # plot a histogram of the created file
    # created_file = ['yes' if score.created_file else 'no' for score in scores.values()]
    # plt.hist(created_file, bins=range(0, 3), align='left', rwidth=0.8)
    # plt.xlabel('File Created')
    # plt.ylabel('Number of Trials')
    # plt.title(f'Frequency of File Created {task_variant}')
    # plt.savefig(workdir/'created_file_histogram.png')
    # plt.show()


    # plot a histogram of correct vs incorrect
    correct = ['correct' if trial_name in successful_trial_names else 'incorrect' for trial_name in scores]
    plt.hist(correct, bins=range(0, 3), align='left', rwidth=0.8)
    plt.xlabel('Success')
    plt.ylabel('Number of Trials')
    plt.title(f'Frequency of Correct Results {task_variant}')
    plt.savefig(workdir/'correct_histogram.png')
    plt.show()


    # make a single unified plot
    correct_num_rows = [score.correct_num_rows for score in scores.values()]
    any_data = [score.any_data for score in scores.values()]
    created_file = [score.created_file for score in scores.values()]
    xs = np.arange(len(scores))
    plt.plot(xs, [trial_name in successful_trial_names for trial_name in scores], label='Trials', marker='x')
    # plt.scatter(xs, correct_num_rows, label='Correct Number of Rows', marker='+')
    # plt.scatter(xs, any_data, label='Any Data', marker='1')
    # plt.scatter(xs, created_file, label='File Created', marker='2')
    plt.xlabel('Trial')
    plt.ylabel('Score')
    plt.title(f' Trial Successes {task_variant}')
    plt.legend()
    plt.savefig(workdir/'combined_scores_plot.png')
    plt.show()


    # plotting of the clustering of the code solutions itself.
    # measure the code spread
    reference_code_path = here / 'gdc_reference_solution.py'
    reference_code = reference_code_path.read_text()
    reference_code = reference_code.split('"""')[-1].strip()  # remove the docstring

    analyzer.plot_code_clusters(reference_code, trials, successful_trials) # mostly just the charts generated are what is of interest


    


    



if __name__ == '__main__':
    main()