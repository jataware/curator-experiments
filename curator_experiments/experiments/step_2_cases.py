from adhoc_api.tool import APISpec
from adhoc_api.loader import load_yaml_api
from pathlib import Path

here = Path(__file__).parent
gdc_folder = here / '../gdc'


def step_2_api() -> APISpec:
    """GDC API with no examples"""
    api = load_yaml_api(gdc_folder/'api_no_examples.yaml')
    api['cache_key'] = 'api_assistant_gdc_no_examples'
    # no examples to add, so leave docs as is
    return api