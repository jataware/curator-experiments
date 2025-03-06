"""
run adhoc api N times with the same query and measure the difference in the results generated
"""


from archytas.react import ReActAgent, FailedTaskError
from adhoc_api.tool import AdhocApi, APISpec
from adhoc_api.loader import load_yaml_api
from adhoc_api.utils import move_to_isolated_dir
from pathlib import Path
from .utils import PythonTool, timeout, TimeoutException, save_to_yaml, CaptureCode

import pdb


here = Path(__file__).parent
gdc_folder = here / '../gdc'



def main():
    with move_to_isolated_dir():
        #TODO: parameterize this with cmdline args (mainly the api selection)
        test_loop(num_trials=100, timeout_seconds=600, api=step_3d_api())



def test_case(query:str, capture_code:CaptureCode, api: APISpec):
    # Set up AdhocApi with GDC API
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
            


def test_loop(num_trials: int, timeout_seconds: int, api: APISpec):
    # query to test repeatability of
    query_template = 'In GDC find all cases of lymphoblastic leukemia with a JAK1 somatic mutation and save the result to a csv named {name}. Please do not print out the result, only save it to the csv file'

    capture_code = CaptureCode()
    for i in range(num_trials):
        print('='*80)
        print(f"Trial {i}")
        capture_code.set_i(i)
        try:
            with timeout(timeout_seconds):
                test_case(query_template.format(name=f'trial_{i}.csv'), capture_code=capture_code, api=api)
        except (Exception, KeyboardInterrupt) as e:
            print(f"Error: {e}")
            capture_code.code[f'trial_{i}'].append(f"Error: {e}")
        save_to_yaml({f'trial_{i}': capture_code.code[f'trial_{i}']}, Path('captured_code.yaml'), append=True)
        print('='*80)



examples_template = """\
# Examples of GDC API Usage

Here are some examples of how to use the API:
{examples}
"""

def update_api_for_trial(api: APISpec, examples_filename: str|None = None, new_cache_key: str|None = None) -> APISpec:
    """Add examples to the API documentation"""
    
    if examples_filename is not None:
        examples = (gdc_folder / examples_filename).read_text()
        api['documentation'] = api['documentation'] + '\n\n\n' + examples_template.format(examples=examples)
    
    if new_cache_key is not None:
        api['cache_key'] = new_cache_key
    
    return api

def step_2_api() -> APISpec:
    """GDC API with no examples"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api['cache_key'] = 'api_assistant_gdc_no_examples'
    # no examples to add, so leave docs as is
    return api

def step_3a_api() -> APISpec:
    """GDC API with a single example that is verbatim the expected solution"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api, 
        examples_filename='examples_(reference_solution).md',
        new_cache_key='api_assistant_gdc_with_reference_solution'
    )
    return api


def step_3b_api() -> APISpec:
    """GDC API with a single example that is slightly different (but still quite similar) to the expected solution"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        'examples_(single_similar_example).md',
        new_cache_key='api_assistant_gdc_with_single_similar_example'
    )
    return api


def step_3c1_api() -> APISpec:
    """GDC API with multiple examples, but shouldn't be enough to overwhelm/saturate the agent"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        'examples_(including_reference_and_others).md',
        new_cache_key='api_assistant_gdc_with_reference_and_multiple_examples'
    )
    return api


def step_3c2_api() -> APISpec:
    """GDC API with multiple examples, but shouldn't be enough to overwhelm/saturate the agent"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        'examples.md',
        new_cache_key='api_assistant_gdc_with_multiple_examples'
    )
    return api


def step_3d_api() -> APISpec:
    """GDC API with too many similar examples that may degrade agent performance"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        'examples_(too_many).md',
        new_cache_key='api_assistant_gdc_with_too_many_examples'
    )
    return api

## ETC cases












if __name__ == "__main__":
    main()