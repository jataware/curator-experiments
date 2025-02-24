"""
run adhoc api N times with the same query and measure the difference in the results generated
"""


from archytas.react import ReActAgent, FailedTaskError
from adhoc_api.tool import AdhocApi
from adhoc_api.loader import load_yaml_api
from adhoc_api.utils import move_to_isolated_dir
# from adhoc_api.python import PythonTool
from archytas.tools import PythonTool as OriginalPythonTool
from pathlib import Path
from collections import defaultdict
import yaml

import pdb


here = Path(__file__).parent


def test(num_trials=10, timeout_seconds=60):
    
    # Set up AdhocApi with GDC API
    api = load_yaml_api(here/'../gdc/api_no_examples.yaml')
    adhoc_api = AdhocApi(
        apis=[api],
        drafter_config={'provider': 'google', 'model': 'gemini-1.5-pro-001'}
        # drafter_config={'provider': 'openai', 'model': 'gpt-4o'}
    )

    # set up the python tool to save any instances of code being run
    class CaptureCode:
        def __init__(self):
            self.i = 0
            self.code = defaultdict(list)
        def set_i(self, i):
            self.i = i
        def __call__(self, code):
            self.code[self.i].append(code)
    capture_code=CaptureCode()
    python = PythonTool(code_side_effect=capture_code)

    # Set up archytas agent
    tools = [adhoc_api, python]


    # query to test repeatability of
    query_template = 'In GDC find all cases of lymphoblastic leukemia with a JAK1 somatic mutation and save the result to a csv named {name}'

    # work in an isolated directory
    with move_to_isolated_dir():
        for i in range(num_trials):
            print('='*80)
            print(f"Trial {i}")
            capture_code.set_i(i)
            agent = ReActAgent(messages=[], model='gpt-4o', tools=tools, verbose=True, allow_ask_user=False)
            query = query_template.format(name=f"trial_{i}.csv")
            try:
                with timeout(timeout_seconds):
                    answer = agent.react(query)
                    print(answer)
            except (FailedTaskError, TimeoutException) as e:
                print(f"Error: {e}")
            
            print('='*80)


    # Save all of the captured code to a file
    with open('captured_code.yaml', 'w') as f:
        yaml.dump(capture_code.code, f)




from archytas.tool_utils import tool
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
def raise_timeout(seconds):
    raise TimeoutException(f"Operation timed out after {seconds} seconds")
@contextmanager
def timeout(seconds):
    print('creating new timeout')
    timer = threading.Timer(interval=seconds, function=raise_timeout, args=(seconds,))
    timer.start()
    try:
        yield
    finally:
        timer.cancel()


# import signal
# from contextlib import contextmanager
# class TimeoutException(Exception): ...
# @contextmanager
# def timeout(seconds):
#     def _timeout_handler(signum, frame):
#         raise TimeoutException(f"Operation timed out after {seconds} seconds")

#     signal.signal(signal.SIGALRM, _timeout_handler)
#     signal.alarm(seconds)
    
#     try:
#         yield
#     finally:
#         signal.alarm(0)  # Disable the alarm





def characterize_deviation():
    pdb.set_trace()











if __name__ == "__main__":
    test()