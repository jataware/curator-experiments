from adhoc_api.tool import APISpec, DrafterConfig
from adhoc_api.loader import load_yaml_api
from pathlib import Path
from .utils import update_api_for_trial


here = Path(__file__).parent
gdc_folder = here / '../gdc'

query_base = 'In GDC find all cases of lymphoblastic leukemia with a JAK1 somatic mutation'
drafter_config = {'provider': 'google', 'model': 'gemini-1.5-pro-001'}


def step_2_api() -> tuple[APISpec, DrafterConfig]:
    """GDC API with no examples"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api['cache_key'] = 'api_assistant_gdc_no_examples'
    # no examples to add, so leave docs as is
    return api, drafter_config


def step_3a_api() -> tuple[APISpec, DrafterConfig]:
    """GDC API with a single example that is verbatim the expected solution"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api, 
        examples_filename='examples_(reference_solution).md',
        new_cache_key='api_assistant_gdc_with_reference_solution'
    )
    return api, drafter_config


def step_3b_api() -> tuple[APISpec, DrafterConfig]:
    """GDC API with a single example that is slightly different (but still quite similar) to the expected solution"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        'examples_(single_similar_example).md',
        new_cache_key='api_assistant_gdc_with_single_similar_example'
    )
    return api, drafter_config


def step_3c1_api() -> tuple[APISpec, DrafterConfig]:
    """GDC API with multiple examples, but shouldn't be enough to overwhelm/saturate the agent"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        'examples_(including_reference_and_others).md',
        new_cache_key='api_assistant_gdc_with_reference_and_multiple_examples'
    )
    return api, drafter_config


def step_3c2_api() -> tuple[APISpec, DrafterConfig]:
    """GDC API with multiple examples, but shouldn't be enough to overwhelm/saturate the agent"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        'examples.md',
        new_cache_key='api_assistant_gdc_with_multiple_examples'
    )
    return api, drafter_config


def step_3d_api() -> tuple[APISpec, DrafterConfig]:
    """GDC API with too many similar examples that may degrade agent performance"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api = update_api_for_trial(
        api,
        'examples_(too_many).md',
        new_cache_key='api_assistant_gdc_with_too_many_examples'
    )
    return api, drafter_config
