from archytas.tool_utils import tool
from archytas.tools import PythonTool as OriginalPythonTool
from typing import Callable
#This is a shim class around the regular PythonTool so that we can capture any time code is run by the agent
class PythonTool:
    """
    Tool for running python code. If the user asks you to write code, you can run it here.
    """
    def __init__(self, code_side_effect: Callable[[str], None]):
        self.tool = OriginalPythonTool()
        self.side_effect = code_side_effect
    @tool()
    def run(self, code: str) -> str:
        """
        Runs python code in a python environment.

        The environment is persistent between runs, so any variables created will be available in subsequent runs.
        The only visible effects of this tool are from output to stdout/stderr. If you want to view a result, you MUST print it.

        Args:
            code (str): The code to run

        Returns:
            str: The stdout output of the code
        """
        self.side_effect(code)
        return self.tool.run(code)



# context manager for quitting if the process takes too long
import threading
from contextlib import contextmanager
class TimeoutException(Exception): ...
def raise_timeout(seconds:float, message:str|None=None):
    msg = f"Operation timed out after {seconds} seconds"
    if message:
        msg += f" with message: {message}"
    raise TimeoutException(msg)
@contextmanager
def timeout(seconds:float, *, message:str|None=None, verbose:bool=False):
    if verbose:
        print('creating new timeout')
    timer = threading.Timer(interval=seconds, function=raise_timeout, args=(seconds, message))
    timer.start()
    try:
        yield
    finally:
        timer.cancel()


from collections import defaultdict
class CaptureCode:
    def __init__(self):
        self.i = 0
        self.code = defaultdict(list)
    def set_i(self, i):
        self.i = i
    def __call__(self, code):
        self.code[f'trial_{self.i}'].append(code)




from pathlib import Path
def save_to_yaml(data: dict[list[str]], filename: Path, append: bool = False):
    #TODO: better formatting of saved code with block lines rather than escaping whitespace
    lines = []
    for trial, codes in data.items():
        lines.append(f"{trial}:")
        for code in codes:
            lines.append(f"  - |")
            for line in code.split('\n'):
                lines.append(f"    {line}")
    
    if append:
        with filename.open('a') as f:
            lines.insert(0, '\n')  # add a newline at the beginning to separate from previous content
            f.write('\n'.join(lines))
        print(f"Appended captured code to {filename}")
    else:
        filename.write_text('\n'.join(lines))
        print(f"Saved captured code to {filename}")



from adhoc_api.tool import APISpec
from pathlib import Path
here = Path(__file__).parent
gdc_folder = here / '../gdc'

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
