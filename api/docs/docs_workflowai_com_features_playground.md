\[todo: add screenshot\] !\[alt text\](assets/Screenshot 2025-01-03 at 15.28.30.png)

Playground is designed to iterate quickly on prompts and models. By default, you can compare 3 models side-by-side.

The playground is composed of 3 sections:

- **Input**: where the input variables are defined.

- **Parameters**: where the prompt and temperature are defined.

- **Outputs**: where the LLM outputs are displayed.


## [Direct link to heading](https://docs.workflowai.com/features/playground\#input)    Input

You can manually enter the input variable, and for text inputs (only), you can use AI to generate synthetic data.

\[video\]

## [Direct link to heading](https://docs.workflowai.com/features/playground\#parameters)    Parameters

You can adjust the prompt and temperature.

### [Direct link to heading](https://docs.workflowai.com/features/playground\#prompt)    Prompt

The prompt is the text of instructions given to the LLM to describe what is expected from the agent.

When you create a new agent, WorkflowAI will generate a default prompt for you. You can manually edit the prompt to customize the task, but our recommanded approach is to use the [AI prompt engineering](https://github.com/WorkflowAI/documentation/blob/main/prompt-engineering/README.md) feature to improve the prompt.

### [Direct link to heading](https://docs.workflowai.com/features/playground\#temperature)    Temperature

Temperature is a parameter that controls the randomness of the LLM's outputs. WorkflowAI provides three preset temperature settings: \[todo: check if smart default temperature per task type is rolled out https://linear.app/workflowai/issue/WOR-681/\[plan\]-suggest-the-right-temperature-for-the-task\]

- **Precise** (Default): The recommended and default setting for all tasks



- Best for tasks requiring accuracy and consistency

- Ideal for factual responses, code generation, or structured data extraction

- Produces reliable, repeatable results


- **Balanced**: Moderate setting that balances creativity and coherence



- Good for general-purpose tasks

- Works well for most conversational and analytical tasks

- Provides reasonable variation while maintaining relevance


- **Creative**: Maximum diversity and exploration



- Best for tasks requiring unique or innovative outputs

- Ideal for brainstorming, creative writing, or generating alternatives

- Produces more varied but potentially less focused results


- **Custom**: User-defined temperature setting



- Allows precise control over the temperature value

- For advanced users who understand the impact of temperature


Note: "Precise" is automatically selected as the default temperature setting for all new tasks to ensure consistent and reliable outputs. You can adjust this in the Parameters section of the Playground if your use case requires more variation.

\[video\]

## [Direct link to heading](https://docs.workflowai.com/features/playground\#outputs)    Outputs

The outputs section displays the LLM outputs.

\[video\]

For each output, WorkflowAI also displays:

- 💰 Cost: The total price in USD for generating this output

- ⚡ Latency: How long it took to get a response from the model, in seconds

- 📊 Context window usage: How much of the model's maximum token limit was used, shown as a percentage


> WorkflowAI Cloud offers a price-match guarantee, meaning that you're not charged more than the price per token of the model you're using. Learn more about the price-match guarantee [here](https://workflowai.com/pricing).

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2FWorkflowAI%2Fdocumentation%2Fblob%2Fmain%2Fdocs%2Ffeatures%2FScreenshot%25202025-01-03%2520at%252015.52.23.png&width=768&dpr=4&quality=100&sign=d0e66441&sv=2)

alt text\|300

## [Direct link to heading](https://docs.workflowai.com/features/playground\#pro-tip)    Pro-tip

You can display 1, 2, or 3 model outputs side-by-side in the playground to focus on a single output, compare two options, or evaluate multiple variations simultaneously.

\[video\]

## [Direct link to heading](https://docs.workflowai.com/features/playground\#diff-mode)    Diff mode

You can enable diff mode to highlight the differences between LLM outputs, making it easy to spot exactly what words or sections changed between different outputs.

\[video\]

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2FWorkflowAI%2Fdocumentation%2Fblob%2Fmain%2Fdocs%2Ffeatures%2FScreenshot%25202025-01-03%2520at%252015.47.42.png&width=768&dpr=4&quality=100&sign=11e29d80&sv=2)

alt text

[Previous@prompt](https://docs.workflowai.com/concepts/prompt) [NextBenchmarks](https://docs.workflowai.com/features/benchmarks)

Last updated 2 months ago

Was this helpful?

* * *