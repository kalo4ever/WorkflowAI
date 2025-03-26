Accessible for product managers, and engineers.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-9567cd51f61f8a9ccc9ce8cc9003be94f9d1a484%252Fbenchmarks.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=ec3e41bd&sv=2)

Benchmarks

When you are building a AI agent, you will often want to compare the performance, cost and latency of different [versions](https://docs.workflowai.com/concepts/versions) of your agent. For example, imagine you are building an agent that translate text into a different language, and you want to compare accuracy of the translation, cost and latency between GPT-4o, GPT-4o-mini, Gemini 1.5 Flash and LLAMA 3.1 (8B).

In this section, we will learn:

- what metrics are compared in benchmarks

- how to leave a first positive or negative review

- how AI reviews are generated

- how to run benchmarks to compare different versions of your agent

- how to adjust how AI reviews are generated


## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent\#metrics)    Metrics

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent\#positive-and-negative-reviews)    Positive and negative reviews

We define a review as the evaluation (positive or negative) given to a specific output of an agent. For example, if you are building a agent that write description of images, a review will be the evaluation given to specific description of an image for a specific agent that generated this description.

WorkflowAI currently only supports **positive** reviews, or **negative** reviews (binary outcome).

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent\#cost)    Cost

**Cost** represents how much (in $) you pay for the agent to perform a task. This is an objective metric that is automatically computed by WorkflowAI.

### [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent\#latency)    Latency

**Latency** measures how long (in seconds) it takes for the agent to perform a task. Like cost, this is an objective metric that is automatically computed by WorkflowAI.

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent\#how-to-leave-a-first-review)    How to leave a first review

From the playground, run your agent and look at the outputs section. Then leave a review by clicking on the thumbs up or thumbs down icon.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-7c49659a4cfdd0d8b233a4d6e1901701b26ba1f2%252Fleave-review.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=2b393ef&sv=2)

Leave a review

Once you leave a review, WorkflowAI will use AI to generate reviews for the other remaining outputs.

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent\#how-ai-reviews-are-generated)    How AI reviews are generated

AI-generated reviews are a feature of WorkflowAI that uses an AI agent to review the outputs of other versions automatically.

For example, let's say you're building an agent that summarizes articles. After you leave your first review on one summary, WorkflowAI will automatically use AI to evaluate and generate reviews for all other summaries produced by different versions of your agent.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-a6c20927c82fa986a00729e6975d1206f5f438c9%252Fplayground-reviews.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=eebdc51f&sv=2)

AI-generated reviews

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent\#running-benchmarks)    Running benchmarks

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent\#adjusting-ai-reviews)    Adjusting AI reviews

[PreviousTesting your AI agent](https://docs.workflowai.com/ai-agents-playbook/testing-your-ai-agent) [NextImproving your AI agent](https://docs.workflowai.com/ai-agents-playbook/improving-your-ai-agent)

Last updated 1 month ago

Was this helpful?

* * *