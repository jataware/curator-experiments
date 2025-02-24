"""
High level goal for solution templates is for any time the agent solves a task
to formalize/regularize the solution and save it for future re-use

From an interfacing point of view, I think each adhoc-api drafter agent needs to be
able to access existing solution. But also so does the archytas/etc. agent interacting
with the users. So perhaps the user asks for something, then the archytas agent asks the
drafter which recognizes it as an existing solved solution, and so says to use:

```python
from some_api.prebaked_solutions import some_xyz
some_xyz(whatever, params, you, need, based, on, the, task)
```

and the drafter should also provide a description with it (i.e. the solution template should have something
that goes with it describing the params/use-case/etc.)
"""


from archytas.react import ReActAgent, FailedTaskError
from easyrepl import REPL
from adhoc_api.tool import AdhocApi, view_filesystem
from adhoc_api.loader import load_yaml_api
from adhoc_api.utils import move_to_isolated_dir
# from adhoc_api.python import PythonTool
from archytas.tools import PythonTool
from pathlib import Path


import pdb


here = Path(__file__).parent


def test():
    python = PythonTool()
    api = load_yaml_api(here/'gdc/api.yaml')
    adhoc_api = AdhocApi(
        apis=[api],
        drafter_config={'provider': 'google', 'model': 'gemini-1.5-pro-001'}
        # drafter_config={'provider': 'openai', 'model': 'gpt-4o'}
    )

    tools = [adhoc_api, python, view_filesystem]
    agent = ReActAgent(model='gpt-4o', tools=tools, verbose=True)
    print(agent.prompt)

    # work in an isolated directory
    with move_to_isolated_dir():
        # REPL to interact with agent
        for query in REPL(history_file='../.chat'):
            try:
                answer = agent.react(query)
                print(answer)
            except FailedTaskError as e:
                print(f"Error: {e}")









def facets_to_enums():
    pdb.set_trace()








if __name__ == "__main__":
    test()