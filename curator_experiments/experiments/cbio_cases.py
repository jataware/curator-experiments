from adhoc_api.tool import APISpec, DrafterConfig
from adhoc_api.loader import load_yaml_api
from pathlib import Path
from .utils import update_api_for_trial


here = Path(__file__).parent
cbioportal_folder = here / '../cbioportal'

drafter_config = {'provider': 'anthropic', 'model': 'claude-3-7-sonnet-latest'}
# drafter_config = {'provider': 'anthropic', 'model': 'claude-3-5-sonnet-latest'}
query_base = 'fetch RNA-seq z-scores for STAT5A and STAT5B across the aml target gdc and aml ohsu 2022 studies'

# candidate task:
# fetch RNA-seq z-scores for STAT5A and STAT5B across the aml target gdc and aml ohsu 2022 studies. save the results to a file
# see example 8 from cbioportal examples

def cbio_trial_4a() -> tuple[APISpec, DrafterConfig, str]:
    """Cbioportal API with no examples"""
    api = load_yaml_api(cbioportal_folder/'api_no_examples.yaml')
    api['cache_key'] = 'api_assistant_cbioportal_no_examples'
    return api, drafter_config, query_base


def cbio_trial_4b() -> tuple[APISpec, DrafterConfig, str]:
    """Cbioportal API with a single example that is verbatim the expected solution"""
    api = load_yaml_api(cbioportal_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api, 
        examples_filepath=cbioportal_folder/'examples_(reference_solution).md',
        new_cache_key='api_assistant_cbioportal_with_reference_solution'
    )
    return api, drafter_config, query_base


# TBD what this example will be...
# def cbio_trail_4c() -> tuple[APISpec, DrafterConfig, str]:
#     """Cbioportal API with a single example that is slightly different (but still quite similar) to the expected solution"""
#     api = load_yaml_api(cbioportal_folder/'api_no_examples.yaml')
#     api = update_api_for_trial(
#         api,
#         examples_filepath=cbioportal_folder/'examples_(single_similar_example).md',
#         new_cache_key='api_assistant_cbioportal_with_single_similar_example'
#     )
#     return api, drafter_config, query_base


def cbio_trial_4c() -> tuple[APISpec, DrafterConfig, str]:
    """Cbioportal API with multiple examples, but shouldn't be enough to overwhelm/saturate the agent"""
    api = load_yaml_api(cbioportal_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        examples_filepath=cbioportal_folder/'examples.md',
        new_cache_key='api_assistant_cbio_with_multiple_examples'
    )
    return api, drafter_config, query_base


# TBD where the too many examples will come from
# def cbio_trial_4d() -> tuple[APISpec, DrafterConfig, str]:
#     """Cbioportal API with too many similar examples that may degrade agent performance"""
#     api = load_yaml_api(cbioportal_folder/'api_no_examples.yaml')
#     api = update_api_for_trial(
#         api,
#         examples_filepath=cbioportal_folder/'examples_(too_many).md',
#         new_cache_key='api_assistant_cbio_with_too_many_examples'
#     )
#     return api, drafter_config, query_base



from archytas.react import ReActAgent, FailedTaskError
from adhoc_api.tool import AdhocApi, APISpec
from adhoc_api.utils import move_to_isolated_dir
from pathlib import Path
from .utils import PythonTool, TimeoutException
from easyrepl import REPL
import pdb
def main():
    with move_to_isolated_dir():
        api = cbio_trial_4a()
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