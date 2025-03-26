> This step can be done by either product or development team.

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#common-issues)    Common issues

There can be a few reasons why the agent is not performing well. You need to identify the root cause, and make some changes accordingly. We've listed the most common reasons below.

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#the-schema-misses-some-input-parameters)    The schema misses some _input_ parameters

Example: a task where a transcript of a discussion is extracting calendar events, but the input is missing the `transcript_time` parameter.

Solution: edit the schema. You can edit the schema via WorkflowAI web-app, or via code directly.

\[expandable\]

- edit via web-app

- edit via code \[end\]


### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#the-schemas-misses-some-output-parameters)    The schemas misses some _output_ parameters

Example: a task where a transcript of a discussion is extracting calendar events, but the output is missing the `event_time` parameter.

Solution: edit the schema. You can edit the schema via WorkflowAI web-app, or via code directly.

\[expandable\]

- edit via web-app

- edit via code \[end\]


### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#the-agent-is-not-able-to-access-the-tools-it-needs)    The agent is not able to access the tools it needs.

Example: if you ask a LLM a question after its training date, without including any @search tool.

Solution: add the tools to the agent.

\[expandable\]

- edit via web-app

- edit via code \[end\]


### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#the-input-output-context-window-is-maxed-out)    the (input, output) context window is maxed out.

Example: if you a ask a LLM to ...

Solution, try a model with larger context window, or reduce the size of the input and output.

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#the-instructions-are-invalid-ambiguous-incomplete)    The instructions are invalid, ambiguous, incomplete..

Example: a task that summarize a text, the user wants bullet points summary, but the instructions are not mentioning this requirement.

Solution: write feedback, test a new prompt.

INSIDE WORKFLOWAI'S OWN AGENTS [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent#inside-workflowais-own-agents)

When you use our feature that re-write the instructions bsaed on feedback, you're using a this \[agent\](https://workflowai.com/agents/1).

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#examples-and-descriptions-are-not-precise)    Examples and descriptions are not precise.

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#the-task-is-too-difficult-for-some-models)    The task is too difficult for some models.

Solution: try a different model, more intelligent.

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#the-task-is-too-difficult-for-all-models)    The task is too difficult for all models.

Example: if you ask a LLM to solve a hypothesis still unsolved in math.

Make sure you've tested the most intelligent models available.

Solution: in that case, you'll need to re-evaluate what your AI agent can do.

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#deploy-a-new-version-of-the-agent)    Deploy a new version of the agent

WorkflowAI makes it easy to deploy new versions of your agents, without changing your code.

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent\#benchmark-new-models)    Benchmark new models

WorkflowAI makes it easy to benchmark new models...

[PreviousEvaluating your AI agent](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent) [NextBest practices](https://docs.workflowai.com/ai-agents-playbook/best-practices)

Last updated 1 month ago

Was this helpful?

* * *