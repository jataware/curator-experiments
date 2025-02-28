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