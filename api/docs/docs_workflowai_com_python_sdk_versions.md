WorkflowAI agents are versioned automatically.

To show how versions work, let's create a new agent that can triage a customer question into different categories.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
from typing import Literal
from pydantic import BaseModel
import workflowai

class Input(BaseModel):
    question: str

class Output(BaseModel):
    category: Literal["billing", "technical", "account", "other"]

@workflowai.agent(id="triage-agent")
async def triage_question(input: Input) -> Output:
    """
    Triage a customer question into different categories.
    """
    ...

await triage_question.run(Input(question="How do I change my billing information?"))
```

You can test this agent yourself on [WorkflowAI](https://workflowai.com/docs/agents/triage-agent/1).

Running this agent for the first time will automatically create a new version of the agent on WorkflowAI.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-3a5b7a52ab7b3503794473b7f9ffa9cf75038c19%252Fversion-1.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=4d41fcf7&sv=2)

Versions

A version is a specific **configuration** of an agent.

WorkflowAI defines two types of (agent) versions:

Version Type

Example

Description

**Major** Versions

1, 2, 3, ...

A major version represents a specific configuration of a agent, including its instructions, temperature, descriptions/examples, and tools.

**Minor** Versions

1.1, 1.2, 1.3, ...

A minor version represents a major version **associated with a specific model** (e.g., OpenAI's GPT-4o-mini).

Now let's create another version of the agent, but this time we'll use a different model.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
@workflowai.agent(
    id="triage-agent",
    model=Model.CLAUDE_3_5_HAIKU_LATEST
)
async def triage_question(input: Input) -> Output:
    """
    Triage a customer question into different categories.
    """
    ...

await triage_question.run(Input(question="How do I change my billing information?"))
```

This will create a new minor version of the agent associated with the `CLAUDE_3_5_HAIKU_LATEST` model.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-0f8ef0e272ae5eea8a6f7af45e7c2e42d7ec476d%252Fversion-1.2.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=cc47a678&sv=2)

Versions that have the same parameters are grouped together

## [Direct link to heading](https://docs.workflowai.com/python-sdk/versions\#major-versions)    Major Versions

Major versions are created when you change the instructions, temperature, descriptions/examples, or tools of an agent.

For example, let's change the instructions of the agent.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
async def triage_question(input: Input) -> Output:
    """
    Triage a customer question into different categories.

    Categories:
    - billing: Questions about payments, invoices, pricing, or subscription changes
    - technical: Questions about API usage, SDK implementation, or technical issues
    - account: Questions about account access, settings, or profile management
    - other: Questions that don't fit into the above categories
    """
    ...
```

Changelog between major versions will be generated automatically.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-2a5b20354acd4ad28a5d3631852eb459a79cfde5%252Fversion-2.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=bc0eff1a&sv=2)

Version 2 with new instructions

## [Direct link to heading](https://docs.workflowai.com/python-sdk/versions\#versions-from-code-version-id-or-a-deployment)    Versions from code, version id, or a deployment

WorkflowAI allows you to refer to a version of an agent from your code, a minor version id, or a deployment.

### [Direct link to heading](https://docs.workflowai.com/python-sdk/versions\#versions-from-code)    Versions from code

Setting a docstring or a model in the `@workflowai.agent` decorator signals the client that the agent parameters are fixed and configured via code.

### [Direct link to heading](https://docs.workflowai.com/python-sdk/versions\#versions-from-version-id)    Versions from version id

Since WorkflowAI automatically saves all versions, you can refer to a minor version by its id.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
# this agent will use the version 2.1
@workflowai.agent(id="triage-agent", version="2.1")
```

You can also go to the [Code](https://workflowai.com/docs/agents/triage-agent/1/code?selectedLanguage=Python) section on WorkflowAI to view the generated code for a specific version.

### [Direct link to heading](https://docs.workflowai.com/python-sdk/versions\#versions-from-a-deployment)    Versions from a deployment

To learn more about deployments, read the [Deployments](https://docs.workflowai.com/features/deployments) section first.

Deployments allow you to refer to a version of an agent's parameters from your code that's managed from WorkflowAI dashboard, allowing you to update the agent's parameters without changing your code.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
# production
@workflowai.agent(id="triage-agent", deployment="production") # or simply @workflowai.agent()

# development
@workflowai.agent(id="triage-agent", deployment="development")

# staging
@workflowai.agent(id="triage-agent", deployment="staging")
```

[PreviousSchemas](https://docs.workflowai.com/python-sdk/schemas) [NextMultimodality](https://docs.workflowai.com/python-sdk/multimodality)

Last updated 10 days ago

Was this helpful?

* * *