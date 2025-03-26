## [Direct link to heading](https://docs.workflowai.com/concepts/tools\#what-are-tools)    What are tools?

Tools enable AI agents to:

**Access External Data**

Web searches, web scraping, databases, APIs, files

**Perform Actions**

Form submissions, code execution, API calls, custom functions

Tools have two forms:

**Custom Tools**

Developer-defined tools.

**Hosted Tools**

WorkflowAI-built tools (e.g., _search-web_, _browser-text_).

Hosted tools do not require any code, or engineering effort. But custom tools will require you to write code to handle the tool calls.

## [Direct link to heading](https://docs.workflowai.com/concepts/tools\#custom-tools)    Custom Tools

Custom tools are tools specific to your application. You are responsible for running these tools when they are called by the AI agent.

### [Direct link to heading](https://docs.workflowai.com/concepts/tools\#add-a-new-tool)    Add a new tool

#### [Direct link to heading](https://docs.workflowai.com/concepts/tools\#using-the-playground)    Using the playground

#### [Direct link to heading](https://docs.workflowai.com/concepts/tools\#using-code)    Using code

Adding a custom tool through code is currently only available with our Python SDK. Read the documentation for [adding custom tools](https://docs.workflowai.com/python-sdk/tools).

### [Direct link to heading](https://docs.workflowai.com/concepts/tools\#handling-tool-calls)    Handling tool calls

When the model returns a tool call, you need to execute the tool and return the result.

## [Direct link to heading](https://docs.workflowai.com/concepts/tools\#hosted-tools)    Hosted Tools

### [Direct link to heading](https://docs.workflowai.com/concepts/tools\#what-hosted-tools-are-available)    What hosted tools are available?

WorklfowAI supports and manages the following tools:

- `@search`: search the web to answer a question

- `@browser-text`: navigate on webpages (text-only)


We're working on adding more tools, if you need any specfic tool, please open a discussion on [GitHub](https://github.com/workflowai/workflowai/discussions/categories/ideas) or contact us on [Slack](https://workflowai.com/slack).

### [Direct link to heading](https://docs.workflowai.com/concepts/tools\#how-to-enable-tools)    How to enable tools?

\[todo: explain how to enable tools\] From the playground, under "Instructions", tap on the tools you want to enable.

\[image\]

### [Direct link to heading](https://docs.workflowai.com/concepts/tools\#how-are-tools-billed)    How are tools billed?

Tools are billed independently from the LLM inference costs.

- `@search` tool: $0.... per search

- `@browser-text` tool: $0.... per webpage


[PreviousRuns](https://docs.workflowai.com/concepts/runs) [Next@prompt](https://docs.workflowai.com/concepts/prompt)

Last updated 10 days ago

Was this helpful?

* * *