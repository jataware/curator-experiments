"""
run adhoc api N times with the same query and measure the difference in the results generated
"""


from archytas.react import ReActAgent, FailedTaskError
from adhoc_api.tool import AdhocApi
from adhoc_api.loader import load_yaml_api
from adhoc_api.utils import move_to_isolated_dir
from pathlib import Path
from .utils import PythonTool, timeout, TimeoutException, save_to_yaml, CaptureCode

import pdb


here = Path(__file__).parent



def main():
    with move_to_isolated_dir():
        test_loop(num_trials=100, timeout_seconds=600)



def test_case(query:str, capture_code:CaptureCode):
    # Set up AdhocApi with GDC API
    api = load_yaml_api(here/'../gdc/api_no_examples.yaml')
    adhoc_api = AdhocApi(
        apis=[api],
        drafter_config={'provider': 'google', 'model': 'gemini-1.5-pro-001'}
    )

    python = PythonTool(code_side_effect=capture_code)

    # Set up archytas agent
    tools = [adhoc_api, python]
    agent = ReActAgent(messages=[], model='gpt-4o', tools=tools, verbose=True, allow_ask_user=False)
    # query = query_template.format(name=f"trial_{i}.csv")
    try:
        answer = agent.react(query)
        print(answer)
    except (FailedTaskError, TimeoutException) as e:
        print(f"Error: {e}")
            


def test_loop(num_trials: int, timeout_seconds: int):
    # query to test repeatability of
    query_template = 'In GDC find all cases of lymphoblastic leukemia with a JAK1 somatic mutation and save the result to a csv named {name}. Please do not print out the result, only save it to the csv file'

    capture_code = CaptureCode()
    for i in range(num_trials):
        print('='*80)
        print(f"Trial {i}")
        capture_code.set_i(i)
        try:
            with timeout(timeout_seconds):
                test_case(query_template.format(name=f'trial_{i}.csv'), capture_code=capture_code)
        except (Exception, KeyboardInterrupt) as e:
            print(f"Error: {e}")
            capture_code.code[f'trial_{i}'].append(f"Error: {e}")
        save_to_yaml({f'trial_{i}': capture_code.code[f'trial_{i}']}, Path('captured_code.yaml'), append=True)
        print('='*80)


# def fix_yaml():
#     # load a yaml file
#     path = here/'../../workdir_20250224_125812/captured_code.yaml'
#     with open(path, 'r') as f:
#         data = yaml.safe_load(f)
    

#     # create a new dict from the yaml
#     fixed_data = {f'trial_{k}':v for k, v in data.items()}
    
#     save_to_yaml(fixed_data, path.parent/'fixed_captured_code.yaml')








def characterize_deviation():
    """
    Approach:
    1. randomly select one example as the reference
    2. have the LLM first rank and then score (0-100) how similar the other examples are to the reference
    3. use the farthest example (and perhaps also the middle (distance-wise)) as a new reference
    4. repeat the process with the new reference
    5. repeat for a few references (perhaps just randomly select references too, or evenly select from the spread of the first ranking)
    6. create vectors for each example being the score distance from the reference 0
    7. use k-means to cluster into groups
    8. can plot and look at the std of each cluster
    """
    pdb.set_trace()











if __name__ == "__main__":
    main()