import yaml
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
from adhoc_api.uaii import ClaudeAgent, OpenAIAgent
from collections import defaultdict

from .utils import timeout


import pdb

here = Path(__file__).parent
workdir = here / '../../workdir_20250225_132405'

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


    # load all the trials
    # workdir = here / '../../workdir_20250225_132405'
    code_path = workdir/'captured_code.yaml'
    trials: dict = yaml.safe_load(code_path.open())

    # measure the code spread
    reference_code_path = here / 'step1.py'
    reference_code = reference_code_path.read_text()
    # code_spread = measure_code_spread(reference_code, trials)
    code_clusters = measure_code_clusters(reference_code, trials)

    # save the score of each trial
    scores: dict[str, Score] = {}

    # compare each of the trials to the reference
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


def measure_code_clusters(reference: str, trials: dict[str, list[str]], N:int=10):
    # Include the reference in the trials
    reference_trial_number = len(trials)
    while f'trial_{reference_trial_number}' in trials:
        reference_trial_number += 1
    reference_name = f'trial_{reference_trial_number}'
    trials = {**trials, reference_name: [reference]}

    primary_ranking = measure_code_spread_trial(reference, trials)
    # select N other evenly spaced trials from the primary ranking
    selections = np.linspace(0, len(primary_ranking)-1, N).astype(int)[1:]
    secondary_references_names = [primary_ranking[i][1] for i in selections]
    secondary_references = ['\n\n############\n\n'.join(trials[name]) for name in secondary_references_names]
    all_secondary_rankings = []
    for secondary_reference in tqdm(secondary_references, desc='measuring secondary references', total=len(secondary_references)):
        try:
            with timeout(300):
                secondary_ranking = measure_code_spread_trial(secondary_reference, trials)
        except Exception as e:
            print(f"Error measuring secondary reference {secondary_reference}: {e}")
            continue
        all_secondary_rankings.append(secondary_ranking)

    # dictionaries for building the feature vectors
    rank_feature_dict: dict[str, list[int]] = defaultdict(list)
    score_feature_dict: dict[str, list[float]] = defaultdict(list)

    all_rankings = [primary_ranking] + all_secondary_rankings
    for rankings in all_rankings:
        # generate a dictionary out of the rankings for easy lookup
        ranking_map: dict[str, tuple[int, float]] = {}
        for rank, name, score in rankings:
            if name in ranking_map: print(f"WARNING: Duplicate name '{name}' in rankings")
            ranking_map[name] = (rank, score)
        
        # add every trial into the rank and scor feature dicts
        for trial_name in trials:
            if trial_name not in ranking_map:
                # if the trial is not in the ranking, add it with a rank of 0 and score of 0
                rank_feature_dict[trial_name].append(-100)
                score_feature_dict[trial_name].append(-100)
                print(f"WARNING: Trial '{trial_name}' not in ranking map. using -100 for rank and score")
            else:
                # otherwise, add the rank and score from the ranking
                rank, score = ranking_map[trial_name]
                rank_feature_dict[trial_name].append(rank)
                score_feature_dict[trial_name].append(score)
    
    # convert the dictionaries to ndarrays
    rank_features = np.array([rank_feature_dict[trial] for trial in trials])
    score_features = np.array([score_feature_dict[trial] for trial in trials])

    solution_trials = ['trial_12', 'trial_24', 'trial_34', 'trial_58']
    solution_indices = [list(trials.keys()).index(trial) for trial in solution_trials]
    reference_index = [list(trials.keys()).index(reference_name)]

    # plot the features using t-sne (2 separate plots). Highlight the solution trials with red x's
    from sklearn.manifold import TSNE
    tsne = TSNE(n_components=2, perplexity=30, n_iter=1000)
    rank_tsne = tsne.fit_transform(rank_features)
    score_tsne = tsne.fit_transform(score_features)
    plt.scatter(rank_tsne[:, 0], rank_tsne[:, 1])
    plt.scatter(rank_tsne[solution_indices, 0], rank_tsne[solution_indices, 1], color='red', marker='x', s=100)
    plt.scatter(rank_tsne[reference_index, 0], rank_tsne[reference_index, 1], color='green', marker='o', s=100)
    plt.legend(['all trials', 'correct solutions'],)
    plt.title('t-SNE of Code Similarity Ranks')
    plt.xlabel('t-SNE 1')
    plt.ylabel('t-SNE 2')
    plt.savefig(workdir/'rank_tsne.png')
    plt.show()
    
    plt.scatter(score_tsne[:, 0], score_tsne[:, 1])
    plt.scatter(score_tsne[solution_indices, 0], score_tsne[solution_indices, 1], color='red', marker='x', s=100)
    plt.scatter(score_tsne[reference_index, 0], score_tsne[reference_index, 1], color='green', marker='o', s=100)
    plt.legend(['all trials', 'correct solutions'],)
    plt.title('t-SNE of Code Similarity Scores')
    plt.xlabel('t-SNE 1')
    plt.ylabel('t-SNE 2')
    plt.savefig(workdir/'score_tsne.png')
    plt.show()

    # All of the above plotting but with PCA instead
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    rank_pca = pca.fit_transform(rank_features)
    score_pca = pca.fit_transform(score_features)
    plt.scatter(rank_pca[:, 0], rank_pca[:, 1])
    plt.scatter(rank_pca[solution_indices, 0], rank_pca[solution_indices, 1], color='red', marker='x', s=100)
    plt.legend(['all trials', 'correct solutions'],)
    plt.title('PCA of Code Similarity Ranks')
    plt.xlabel('PCA 1')
    plt.ylabel('PCA 2')
    plt.savefig(workdir/'rank_pca.png')
    plt.show()

    plt.scatter(score_pca[:, 0], score_pca[:, 1])
    plt.scatter(score_pca[solution_indices, 0], score_pca[solution_indices, 1], color='red', marker='x', s=100)
    plt.legend(['all trials', 'correct solutions'],)
    plt.title('PCA of Code Similarity Scores')
    plt.xlabel('PCA 1')
    plt.ylabel('PCA 2')
    plt.savefig(workdir/'score_pca.png')
    plt.show()

    
    pdb.set_trace()
    ...

def measure_code_spread(reference: str, trials: dict[str, list[str]], n_repeats: int = 10) -> list[tuple[int, str, float]]:
    all_rankings = [measure_code_spread_trial(reference, trials) for _ in tqdm(range(n_repeats), desc='Collecting Code Spread Trials', total=n_repeats)]

    rank_map = defaultdict(list)
    for rankings in all_rankings:
        for trial in rankings:
            rank, name, score = trial
            rank_map[name].append((rank, score))

    # compute the average rank and score for each trial
    averages = []
    for name in rank_map:
        avg_rank = np.mean([rank for rank, _ in rank_map[name]])
        avg_score = np.mean([score for _, score in rank_map[name]])
        averages.append((avg_rank, name, avg_score))
    
    # sort the averages by the new rank (TBD, could sort by score instead)
    averages.sort(key=lambda x: x[0])

    # DEBUG printout
    for i, (rank, name, score) in enumerate(averages):
        print(f"{i}: {name} - {score}")

    # plot the distribution of the scores
    scores = [score for _, _, score in averages]
    plt.hist(scores, bins=range(0, 101, 10), align='left', rwidth=0.8)
    plt.xticks(range(0, 101, 10))
    plt.xlabel('Code Similarity Score')
    plt.ylabel('Number of Trials')
    plt.title('Code Similarity Compared to Reference (No Examples Case)')
    # workdir = here / '../../workdir_20250225_132405'
    plt.savefig(workdir/'code_spread_histogram.png')
    plt.show()


    return averages


def measure_code_spread_trial(reference: str, trials: dict[str, list[str]]) -> list[tuple[int, str, float]]:
    # convert the trials to one string per trial:
    trials = {trial: '\n\n############\n\n'.join(code_chunks) for trial, code_chunks in trials.items()}
    trail_joiner = '\n\n' + '-'*80 + '\n\n'
    trials_str = trail_joiner.join([f"{trial}:\n```\n{code}\n```" for trial, code in trials.items()])
    # print(trials_str)

    # agent = ClaudeAgent(model='claude-3-5-sonnet-latest', system_prompt='you are a python expert helping to analyze code')
    agent = OpenAIAgent(model='gpt-4o', system_prompt='you are a python expert helping to analyze code')
    res = agent.message(f'''\
I have reference code for solving a task to collect data from GDC.
Additionally I have a large collection of attempts/trials to solve the same problem, where each trial may or may not correctly solve the problem.

I want you to rank and score for each trial, how similar it is (code-wise) to the reference, relative to all the other trials.
Basically this is sort of like taking the diff between the reference and solutions. But it is a very rich diff, e.g. if we could parse each solution into it's AST, and then directly compare how similar the ASTs are to eachother. That's what I want you to do conceptually by looking at the code.
A score of 100 means it is completely identical to the reference solution (modulo differences in whitespace and comments). The solution approach used the exact same programming constructs, and if run, it's result would be indistinguishable from the reference solution.
A score of 0 means it is completely different from the reference solution, not solving the same problem, not even in the same language. Just so woefully different there is absolutely nothing of similarity between the it and the reference. Generally you will not give 0s since most solutions will be in the right language.
Scores in between should be based on the style, approach, language features used, expected inputs/outputs, etc. Basically use your best judgement to quantify how similar how the trial solves the problem is to how the reference solves the problem.
e.g. a score of 95 might mean the trial is very close to the reference, just with some renamed variables or slightly different metadata
e.g. a score of 80 might mean the trial is largely taking the same approach as the reference just with a few key differences
Note that some of the trials may include error messages that resulted from running the code. You can ignore those for this analysis.
Also note some of the trials might have multiple attempts at solving the problem. Multiple attempts is points off for similarity, but if the attempts themselves are still quite similar to the reference, that gets a higher score.
So your output should be a list of the trial names with their score in order of your ranking from most similar to the reference to least similar.
Please format your output as just <trial name>: <score> on a new line with no other punctuation or text.
For example, you might output the following:
trial_34: 98
trial_1: 97
trial_7: 65
trial_16: 65
... # all other trials in your ranked order...
trial_28: 51
trial 30: 50
trial_2: 47

Here is the reference solution:
```
{reference}
```

and here are each of the trails:
{trials_str}
                        
Please output your rankings and scores. Please do not include any other text or formatting in your output.
''')
    rankings = []
    lines = [*filter(lambda x: x.strip(), res.splitlines())]
    for i, line in enumerate(lines):
        trial, score = line.split(':')
        rankings.append((i, trial.strip(), float(score.strip())))
        # print(f"{i}: {trial} - {score}")  #DEBUG printout

    return rankings
    
    # print(res)
    pdb.set_trace()
    # for i in res:
    #     print(i, end='')
    # print()
    # pdb.set_trace()
    # ...







if __name__ == '__main__':
    main()