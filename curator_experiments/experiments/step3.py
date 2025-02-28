"""
3a: give the reference solution in examples. null hypothesis is that most cases should be successes
3b: give the similar example and see how that does
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
    api = load_yaml_api(here/'../gdc/api_with_reference_solution_as_single_example.yaml')
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


if __name__ == '__main__':
    main()