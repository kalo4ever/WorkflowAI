### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#building-your-first-ai-agent-in-a-few-minutes)    Building your first AI agent, in a few minutes.

> for product and engineering teams

First goal is to set something running quickly, a POC (Proof of Concept) to validate that AI is able to do what you want, without aiming for perfect results all the time, but getting a first feel of what is possible, or not.

To create a first version of a new agent, you'll only need to be able to describe in a few sentences what the agent should do.

We recommend starting using the [web-app](https://workflowai.com/), as it's the fastest way to get started.

#### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#new-ai-agent)    New AI agent

Tap "+ New AI agent" on the web-app, then pick from the list of suggested AI agents, or write a few sentences describing what the agent should do.

#### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#a-first-schema)    A first schema

WorkflowAI will automatically generate a first schema based on your description.

A schema is a definition of the (input, output) of your agent. For example, if you want an agent to summarize a text, the input is a text, and the output is a summary. If you want the agent to summarize a text in a language that is dependent on the context, you'll need to add a language parameter to the input. The input is like all the variables the LLM will have access to. The output is the different fields the LLM will generate.

Don't focus on the first schema being perfect, you'll likely iterate on the schema multiple times. WorkflowAI handles very well multiple schemas per AI agent, so you can easily edit the schema later.

Once you're happy with your first schema, tap "Save and Try in Playground".

WorkflowAI will automatically:

- generate the first instructions for the AI agent

- generate a input (using synthetic data generation)


Congratulations, your AI agent is running! Now you can iterate on it from the playground.

INSIDE WORKFLOWAI'S OWN AGENTS [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent#inside-workflowais-own-agents)

\- instructions generation - synthetic data generation

\[info\] Make sure the first input reflects what production data will look like. You can use "Generate" or "Import" \[/info\]

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#first-iterations)    First iterations

> This step can be done by either product or development team.

The playground has been designed to quickly iterate on your agent. We recommend you take the following steps to adjust how your AI agent behaves.

#### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#clear-output-fields-descriptions)    Clear output fields descriptions

The first step is to make sure the descriptions are clear and complete. Descriptions are helping the LLM to understand what the input and the output are. WorkflowAI will use AI to generate the descriptions, but you can also edit them manually.

#### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#specific-output-fields-examples)    Specific output fields examples

Examples are very powerful way to help the LLM understand what the output should look like.

#### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#try-different-models)    Try different models

Get a first feel of what models are performing well, and don't hesitate to try multiple models.

#### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#temperature)    Temperature

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent\#ai-assisted-prompt-engineering)    AI-assisted Prompt Engineering

WorkflowAI includes a AI-assisted prompt engineering feature.

Explain \[write feedback\] -- scope: can update instructions, but also fields description and example.

At this point, our AI agent should be working! If you can't get the output you want, go to step

[PreviousWhat is an AI agent?](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent) [NextTesting your AI agent](https://docs.workflowai.com/ai-agents-playbook/testing-your-ai-agent)

Last updated 1 month ago

Was this helpful?

* * *