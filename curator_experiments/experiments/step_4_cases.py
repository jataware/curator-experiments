from adhoc_api.tool import APISpec
from adhoc_api.loader import load_yaml_api
from pathlib import Path
from .utils import update_api_for_trial


here = Path(__file__).parent
cbioportal_folder = here / '../cbioportal'


# candidate task:
# fetch RNA-seq z-scores for STAT5A and STAT5B across the aml target gdc and aml ohsu 2022 studies. save the results to a file
# see example 8 from cbioportal examples

def step_4a_api() -> APISpec:
    """Cbioportal API with no examples"""
    api = load_yaml_api(cbioportal_folder/'api_no_examples.yaml')
    api['cache_key'] = 'api_assistant_cbioportal_no_examples'
    return api


# def step_4b_api() -> APISpec:
#     """GDC API with a single example that is verbatim the expected solution"""
#     api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
#     api = update_api_for_trial(
#         api, 
#         examples_filename='examples_(reference_solution).md',
#         new_cache_key='api_assistant_gdc_with_reference_solution'
#     )
#     return api


from archytas.react import ReActAgent, FailedTaskError
from adhoc_api.tool import AdhocApi, APISpec
from adhoc_api.utils import move_to_isolated_dir
from pathlib import Path
from .utils import PythonTool, TimeoutException
from easyrepl import REPL
import pdb
def main():
    with move_to_isolated_dir():
        api = step_4a_api()
        adhoc_api = AdhocApi(
            apis=[api],
            drafter_config={'provider': 'anthropic', 'model': 'claude-3-5-sonnet-latest'}
        )

        python = PythonTool(code_side_effect=lambda _: None)

        # Set up archytas agent
        tools = [adhoc_api, python]
        agent = ReActAgent(messages=[], model='gpt-4o', tools=tools, verbose=True, allow_ask_user=False)
        
        for query in REPL(history_file=here/'../.chat'):
            try:
                answer = agent.react(query)
                print(answer)
            except (FailedTaskError, TimeoutException) as e:
                print(f"Error: {e}")
                


if __name__ == '__main__':
    main()