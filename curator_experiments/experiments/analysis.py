import yaml
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np


import pdb

here = Path(__file__).parent

def main():
    analyze_step2()


@dataclass
class Score:
    correct_ids: float
    correct_num_rows: bool
    any_data: bool
    created_file: bool
    # code_match: float #TODO: future will have an agent compare the code

def analyze_step2():
    # load the reference solution
    reference_path = here / 'ssm_occurrences_lymphoblastic_leukemia_JAK1.csv'
    reference = pd.read_csv(reference_path)
    solution_ids = set(reference['id'].tolist())
    
    # save the score of each trial
    scores: dict[str, Score] = {}

    # load each of the trials and compare to the reference
    workdir = here / '../../workdir_20250225_132405'
    code_path = workdir/'captured_code.yaml'
    trials: dict = yaml.safe_load(code_path.open())
    for trial, code_chunks in tqdm(trials.items(), desc='Analyzing trials', total=len(trials)):
        data_path = workdir/f'{trial}.csv'
        
        # see if a file was even created
        if not data_path.exists():
            scores[trial] = Score(0, False, False, False)
            continue
            
        # see if the file is empty
        try:
            data = pd.read_csv(data_path)
        except pd.errors.EmptyDataError:
            scores[trial] = Score(0, False, False, True)
            continue
            
        correct_num_rows = len(data) == len(reference)
        any_data = len(data) > 0
        
        try:
            data_ids = set(data['id'].tolist())
        except KeyError:
            # no id column, so just check the raw text from the file
            raw_text = data_path.read_text()
            data_ids = set([id for id in solution_ids if id in raw_text])

        # see if the ids are correct
        correct_ids = len(solution_ids.intersection(data_ids)) / len(solution_ids)

        #TODO: analyze the code chunks for how well they match
        # code_chunks...


        # save the score
        scores[trial] = Score(correct_ids, correct_num_rows, any_data, True)

    
    # print out a map from each result to the frequency of the result
    correct_id_counts = [int(score.correct_ids * 8) for score in scores.values()]
    correct_id_scores = set(correct_id_counts)
    correct_id_freqs = {score: correct_id_counts.count(score) for score in correct_id_scores}
    print(f"Correct ID Frequencies: {correct_id_freqs}")
    
    # # plot a histogram of the id match %
    # plt.hist(correct_id_counts, bins=range(0, 10), align='left', rwidth=0.8)
    # plt.xticks(range(0, 9))
    # plt.xlabel(f'Number of Correct IDs (max {len(solution_ids)})')
    # plt.ylabel('Number of Trials')
    # plt.title('Frequency of Correct Results (No Examples Case)')
    # plt.savefig(workdir/'correct_ids_histogram.png')
    # plt.show()

    # # plot a histogram of the number of rows
    # num_rows = ['correct' if score.correct_num_rows else 'incorrect' for score in scores.values()]
    # plt.hist(num_rows, bins=range(0, 3), align='left', rwidth=0.8)
    # plt.xlabel('Number of Rows in Result')
    # plt.ylabel('Number of Trials')
    # plt.title('Frequency of Correct Number of Rows (No Examples Case)')
    # plt.savefig(workdir/'num_rows_histogram.png')
    # plt.show()

    # # plot a histogram of the any data
    # any_data = ['yes' if score.any_data else 'no' for score in scores.values()]
    # plt.hist(any_data, bins=range(0, 3), align='left', rwidth=0.8)
    # plt.xlabel('Any Data in Result')
    # plt.ylabel('Number of Trials')
    # plt.title('Frequency of Any Data in Result (No Examples Case)')
    # plt.savefig(workdir/'any_data_histogram.png')
    # plt.show()

    # # plot a histogram of the created file
    # created_file = ['yes' if score.created_file else 'no' for score in scores.values()]
    # plt.hist(created_file, bins=range(0, 3), align='left', rwidth=0.8)
    # plt.xlabel('File Created')
    # plt.ylabel('Number of Trials')
    # plt.title('Frequency of File Created (No Examples Case)')
    # plt.savefig(workdir/'created_file_histogram.png')
    # plt.show()


    # make a single unified plot
    correct_num_rows = [score.correct_num_rows for score in scores.values()]
    any_data = [score.any_data for score in scores.values()]
    created_file = [score.created_file for score in scores.values()]
    xs = np.arange(len(scores))
    plt.plot(xs, [int(i==8) for i in correct_id_counts], label='Correct IDs', marker='x')
    # plt.scatter(xs, correct_num_rows, label='Correct Number of Rows', marker='+')
    # plt.scatter(xs, any_data, label='Any Data', marker='1')
    # plt.scatter(xs, created_file, label='File Created', marker='2')
    plt.xlabel('Trial')
    plt.ylabel('Score')
    plt.title('Scores for Each Trial (No Examples Case)')
    plt.legend()
    plt.savefig(workdir/'combined_scores_plot.png')
    plt.show()


    # TODO: plotting of the clustering of the code solutions itself. 








if __name__ == '__main__':
    main()