from adhoc_api.tool import APISpec
from adhoc_api.loader import load_yaml_api
from pathlib import Path
from .utils import update_api_for_trial


here = Path(__file__).parent
gdc_folder = here / '../gdc'


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
