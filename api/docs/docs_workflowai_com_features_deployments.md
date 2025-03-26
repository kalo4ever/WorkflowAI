Deploy specific versions of an agent with ease, allowing for updates to prompts and models **without any code changes**.

## [Direct link to heading](https://docs.workflowai.com/features/deployments\#why-use-deployments)    Why use deployments?

- ✅ update to a new model or prompt without asking your engineering team.

- ✅ save cost by updating to a more recent, cheaper model, without changing your code.

- ✅ improve the quality of your tasks outputs by adjusting the prompt, in real-time, based on users' feedback.

- ✅ use different versions of a task in different environments (development, staging, production).


## [Direct link to heading](https://docs.workflowai.com/features/deployments\#how-to-deploy-a-version)    How to deploy a version?

\[video\]

- Go to "Deployments" section from the menu.

- Pick the environment you want to deploy to, either: production, staging, or development.

- Tap \[Deploy Version\]

- Select the version you want to deploy.

- Tap \[Deploy\]


To avoid any breaking changes: deployments are **schema specific**, meaning that you can deploy a (development, staging, production) version for each schema of an agent.

## [Direct link to heading](https://docs.workflowai.com/features/deployments\#using-your-own-ai-providers-api)    Using your own AI Providers API

### [Direct link to heading](https://docs.workflowai.com/features/deployments\#when-to-use-your-own-api-key)    When to use your own API key?

- if you have custom **zero day** data-retention agreement. Note that WorkflowAI Cloud has signed contratuals agreements with all AI providers that prohibit the use of customer data to train their models.

- if you have credits from [Microsoft Startups](https://startups.microsoft.com/), [Google AI credits](https://cloud.google.com/startup), or [Amazon Bedrock credits](https://aws.amazon.com/startups/credits).

- if you want to use your own rate limits.


Remember that WorkflowAI Cloud offers a price-match guarantee, meaning that you're not charged more than the price per token of the model you're using. Learn more about the price-match guarantee [here](https://docs.workflowai.com/workflowai-cloud/pricing).

## [Direct link to heading](https://docs.workflowai.com/features/deployments\#how-to-use-your-own-api-key)    How to use your own API key?

- Go to "Deployments" section from the menu.

- Tap \[Manage Provider Keys\]

- Select the provider you want to use.

- Enter your API key.

- Tap \[Save\]


> Security: when using WorkflowAI Cloud, your API keys are encrypted at rest.

When you're using your own API keys, WorkflowAI Cloud will not charge you for the LLM calls or storage of runs, but you can get charged for other features (tools like `web-search` and `browser-text` for example, pricing is available [here](https://docs.workflowai.com/features/deployments)).

[PreviousCode](https://docs.workflowai.com/features/code) [NextMonitoring](https://docs.workflowai.com/features/monitoring)

Last updated 1 month ago

Was this helpful?

* * *