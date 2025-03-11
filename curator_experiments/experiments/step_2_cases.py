from adhoc_api.tool import APISpec, DrafterConfig
from adhoc_api.loader import load_yaml_api
from pathlib import Path

here = Path(__file__).parent
gdc_folder = here / '../gdc'

drafter_config = {'provider': 'google', 'model': 'gemini-1.5-pro-001'}

def step_2_api() -> tuple[APISpec, DrafterConfig]:
    """GDC API with no examples"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api['cache_key'] = 'api_assistant_gdc_no_examples'
    # no examples to add, so leave docs as is
    return api, drafter_config