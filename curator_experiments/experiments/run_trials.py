"""
run adhoc api N times with the same query and measure the difference in the results generated
"""


from archytas.react import ReActAgent, FailedTaskError
from adhoc_api.tool import AdhocApi, APISpec, DrafterConfig
from adhoc_api.utils import move_to_isolated_dir
from pathlib import Path
from .utils import PythonTool, timeout, TimeoutException, save_to_yaml, CaptureCode
from .gdc_cases import gdc_trial_2, gdc_trial_3a, gdc_trial_3b, gdc_trial_3c1, gdc_trial_3c2, gdc_trial_3d
from .cbio_cases import cbio_trial_4a, cbio_trial_4b, cbio_trial_4c

import pdb


here = Path(__file__).parent



def main():
    with move_to_isolated_dir():
        #TODO: parameterize this with cmdline args (mainly the api selection)
        api, drafter_config, query_base = cbio_trial_4b()
        test_loop(
            num_trials=100,
            timeout_seconds=600,
            api=api,
            drafter_config=drafter_config,
            query_base=query_base
        )



def test_case(query:str, capture_code:CaptureCode, api: APISpec, drafter_config: DrafterConfig):
    # Set up AdhocApi with GDC API
    adhoc_api = AdhocApi(apis=[api], drafter_config=drafter_config)

    python = PythonTool(code_side_effect=capture_code)

    # Set up archytas agent
    tools = [adhoc_api, python]
    agent = ReActAgent(messages=[], model='gpt-4o', tools=tools, verbose=True, allow_ask_user=False)

    try:
        answer = agent.react(query)
        print(answer)
    except (FailedTaskError, TimeoutException) as e:
        print(f"Error: {e}")
            


def test_loop(num_trials: int, timeout_seconds: int, api: APISpec, drafter_config: DrafterConfig, query_base: str):
    # query to test repeatability of
    query_template = query_base + ' and save the result to a csv named {name}. Please do not print out the result, only save it to the csv file'

    # if ctrl-c occurs 2x in a row, exit program
    interrupted_prev = False 

    # keep track of code snippets executed
    capture_code = CaptureCode()
    
    # Trials Loop
    for i in range(num_trials):
        interrupted_cur = False
        print('='*80)
        print(f"Trial {i}")
        capture_code.set_i(i)
        
        # attempt to run the test case
        try:
            with timeout(timeout_seconds):
                test_case(query_template.format(name=f'trial_{i}.csv'), capture_code=capture_code, api=api, drafter_config=drafter_config)
        
        # handle exceptions
        except (Exception, KeyboardInterrupt) as e:
            print(f"Error: {e}")
            capture_code.code[f'trial_{i}'].append(f"Error: {e}")
            if isinstance(e, KeyboardInterrupt):
                interrupted_cur = True

        # save anything captured to yaml
        finally:
            save_to_yaml({f'trial_{i}': capture_code.code[f'trial_{i}']}, Path('captured_code.yaml'), append=True)
            print('='*80)

        # if we interrupted twice in a row, exit the program
        if interrupted_cur and interrupted_prev:
            print("Exiting program")
            break
        interrupted_prev = interrupted_cur









if __name__ == "__main__":
    main()