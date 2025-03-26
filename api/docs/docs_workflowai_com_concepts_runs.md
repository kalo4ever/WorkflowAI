A run is a single execution of an agent. By default, WorkflowAI stores all runs, available in the "Runs" section.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2FWorkflowAI%2Fdocumentation%2Fblob%2Fmain%2Fdocs%2Fconcepts%2FScreenshot%25202025-01-03%2520at%252017.04.12.png&width=768&dpr=4&quality=100&sign=5da4c9fa&sv=2)

alt text

## [Direct link to heading](https://docs.workflowai.com/concepts/runs\#why-storing-all-runs)    Why storing all runs?

- **Observability**: Understand how the AI is performing by tracking and analyzing its outputs over time.

- **Saving cost**: For the same input and model versions, cached runs can be served without triggering a new LLM call, reducing costs to $0 for serving cached runs.

- **Fine-Tuning and distillation**: Saving all runs is required for fine-tuning models and distillation processes.


## [Direct link to heading](https://docs.workflowai.com/concepts/runs\#how-to-search-runs)    How to search runs?

WorkflowAI provides a powerful search – available under the "Runs" section – to find specific runs:

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2FWorkflowAI%2Fdocumentation%2Fblob%2Fmain%2Fdocs%2Fconcepts%2FScreenshot%25202025-01-03%2520at%252017.11.48.png&width=768&dpr=4&quality=100&sign=ce6ddc1&sv=2)

alt text

> Architecture: under the hood, runs are stored in a Clickhouse database, which is optimized for handling large amount of data, and for fast search and aggregation queries. Clickhouse also compresses data, which reduces storage costs. Learn more about Clickhouse [here](https://clickhouse.com/docs/en/introduction).

## [Direct link to heading](https://docs.workflowai.com/concepts/runs\#view-a-run)    View a run

## [Direct link to heading](https://docs.workflowai.com/concepts/runs\#view-a-run-prompt)    View a run prompt

## [Direct link to heading](https://docs.workflowai.com/concepts/runs\#try-in-playground)    Try in playground

[PreviousVersions](https://docs.workflowai.com/concepts/versions) [NextTools](https://docs.workflowai.com/concepts/tools)

Last updated 2 months ago

Was this helpful?

* * *