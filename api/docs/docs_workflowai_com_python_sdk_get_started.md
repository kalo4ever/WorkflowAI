For engineers.

WorkflowAI Python SDK is a library that allows you to programmatically create and run agents in Python, while being able to use the full power of the WorkflowAI platform.

## [Direct link to heading](https://docs.workflowai.com/python-sdk/get-started\#install-the-sdk)    Install the SDK

`workflowai` requires Python >= 3.9.

[![](https://img.shields.io/pypi/v/workflowai.svg)](https://pypi.org/project/workflowai/)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
pip install workflowai
```

## [Direct link to heading](https://docs.workflowai.com/python-sdk/get-started\#api-key)    API Key

Get your API key from your [WorkflowAI Cloud dashboard](https://workflowai.com/organization/settings/api-keys) or from your self-hosted WorkflowAI dashboard.

Set the `WORKFLOWAI_API_KEY` environment variable.

## [Direct link to heading](https://docs.workflowai.com/python-sdk/get-started\#initialize-the-sdk)    Initialize the SDK

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
import os
import workflowai

workflowai.init( # This initialization is optional when using default settings
    api_key=os.environ.get("WORKFLOWAI_API_KEY"),  # This is the default and can be omitted
    url="https://run.workflowai.com",  # This is the default and can be omitted
)
```

`run.workflowai.com` is our [globally distributed, highly available endpoint](https://docs.workflowai.com/workflowai-cloud/reliability)

You can also set the `WORKFLOWAI_API_URL` environment variable to point to your self-hosted WorkflowAI.

## [Direct link to heading](https://docs.workflowai.com/python-sdk/get-started\#write-your-first-agent)    Write your first agent

An agent is in essence an async function with the added constraints that:

- it has a single argument that is a Pydantic model, which is the input to the agent

- it has a single return value that is a Pydantic model, which is the output of the agent

- it is decorated with the `@workflowai.agent()` decorator


[Pydantic](https://docs.pydantic.dev/latest/) is a very popular and powerful library for data validation and parsing.

The following agent, given a city, returns the country, capital, and a fun fact about the city.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
import workflowai
from pydantic import BaseModel
from workflowai import Model

class CityInput(BaseModel):
    city: str

class CapitalOutput(BaseModel):
    country: str
    capital: str
    fun_fact: str

@workflowai.agent()
async def get_capital_info(city_input: CityInput) -> CapitalOutput:
    ...
```

OpenAIAnthropicGeminiOpenAI (stream)

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
output = await get_capital_info.run(
    CityInput(city="New York"),
    model=Model.GPT_4_LATEST
)
print(output)

# {
#   "country": "United States",
#   "capital": "Washington, D.C.",
#   "fun_fact": "New York City is known as 'The Big Apple' and is famous for its cultural diversity and iconic landmarks like Times Square and Central Park."
# }
# ==================================================
# Cost: $ 0.00091
# Latency: 1.65s
```

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
output = await get_capital_info.run(
    CityInput(city="New York"),
    model=Model.CLAUDE_3_5_SONNET_LATEST
)
print(output)

# Output:
# ==================================================
# {
#   "country": "United States",
#   "capital": "Washington, D.C.",
#   "fun_fact": "New York City's Federal Reserve Bank has the largest gold storage in the world, containing approximately 7,000 tons of gold bullion stored 80 feet below street level."
# }
# ==================================================
# Cost: $ 0.001755
# Latency: 2.43s
```

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
output = await get_capital_info.run(
    CityInput(city="New York"),
    model=Model.GEMINI_2_0_FLASH_LATEST
)
print(output)

# Output:
# ==================================================
# {
#   "country": "United States of America",
#   "capital": "Washington, D.C.",
#   "fun_fact": "New York City is home to over 8 million people and over 800 languages are spoken in New York City, making it the most linguistically diverse city in the world."
# }
# ==================================================
# Cost: $ 0.00005
# Latency: 1.26s
```

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
# use `.stream()` to stream the output
async for chunk in get_capital_info.stream(
    CityInput(city="New York"),
    model=Model.GPT_4O_MINI_LATEST
):
    print(chunk)

# {
#   "country": "United"
# }
# {
#   "country": "United States"
# }
# {
#   "country": "United States"
#   "capital": "Washington"
# }
# streaming continues...
# ...
```

You have created your first agent! Congratulations.

Agents created by the SDK are also available in the [Playground](https://workflowai.com/docs/agents/get-capital-info/1).

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-d2cd8c45d767a51f39d8edd56285d652fd0b6ec4%252Fdocs-capital-info.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=a82222c6&sv=2)

Playground

Runs are automatically logged as well from the [Runs](https://workflowai.com/docs/agents/get-capital-info/1/runs?page=0) section.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-2b863fdeb62788a2a1915bdc943a0b0f6d68fba5%252Fdocs-capital-info.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=c9f17e4f&sv=2)

Runs

## [Direct link to heading](https://docs.workflowai.com/python-sdk/get-started\#next-steps)    Next steps

Let's go through in more detail [how to setup an agent](https://docs.workflowai.com/python-sdk/agent).

[PreviousCompliance](https://docs.workflowai.com/workflowai-cloud/compliance) [Next@workflowai.agent](https://docs.workflowai.com/python-sdk/agent)

Last updated 10 days ago

Was this helpful?

* * *