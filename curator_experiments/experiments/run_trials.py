"""
run adhoc api N times with the same query and measure the difference in the results generated
"""


from archytas.react import ReActAgent, FailedTaskError
from adhoc_api.tool import AdhocApi, APISpec
from adhoc_api.utils import move_to_isolated_dir
from pathlib import Path
from .utils import PythonTool, timeout, TimeoutException, save_to_yaml, CaptureCode
from .step_2_cases import step_2_api
from .step_3_cases import step_3a_api, step_3b_api, step_3c1_api, step_3c2_api, step_3d_api


import pdb


here = Path(__file__).parent
gdc_folder = here / '../gdc'



def main():
    with move_to_isolated_dir():
        #TODO: parameterize this with cmdline args (mainly the api selection)
        test_loop(num_trials=100, timeout_seconds=600, api=step_3c1_api())



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








if __name__ == "__main__":
    main()