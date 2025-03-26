### [Direct link to heading](https://docs.workflowai.com/workflowai-cloud/reliability\#reliability)    Reliability

[![](https://uptime.betterstack.com/status-badges/v2/monitor/1cuxx.svg)](https://status.workflowai.com/)

Our goal with WorkflowAI Cloud is to provide a 100% uptime on our API endpoint that is used for running an AI agent.

We've designed our architecture to be resilient in a few ways:

- at the AI provider level, we implemented a fallback mechanism that brings redundacy. For example, if OpenAI API is down, WorkflowAI will automatically switch to Azure OpenAI API.

- at the API level, we run our inference API `run.workflowai.com` in a separate container, isolated from the rest of our other API endpoints.

- at the database level, we use a multi-region database to ensure that your data is always available.

- at the datacenter level, we bring redundacy by running our API in multiple independant regions.


### [Direct link to heading](https://docs.workflowai.com/workflowai-cloud/reliability\#ai-provider-fallback)    AI provider fallback

\[explain more about AI provider fallback\]

### [Direct link to heading](https://docs.workflowai.com/workflowai-cloud/reliability\#database-redundacy)    Database redundacy

\[explain more about database redundacy\] We use MongoDB Atlas, and we have a multi region cluster.

### [Direct link to heading](https://docs.workflowai.com/workflowai-cloud/reliability\#datacenter-redundacy)    Datacenter redundacy

\[explain more about datacenter redundacy\]

Azure Front Door

[PreviousPricing](https://docs.workflowai.com/workflowai-cloud/pricing) [NextCompliance](https://docs.workflowai.com/workflowai-cloud/compliance)

Last updated 1 month ago

Was this helpful?

* * *