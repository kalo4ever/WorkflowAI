Integrate WorkflowAI with v0.dev to enable AI agents in your app.

## [Direct link to heading](https://docs.workflowai.com/getting-started/for-developers/v0.dev\#quick-guide)    Quick guide

1

#### [Direct link to heading](https://docs.workflowai.com/getting-started/for-developers/v0.dev\#create-an-agent)    Create an agent

Create an agent in WorkflowAI, like you would normally do.

2

#### [Direct link to heading](https://docs.workflowai.com/getting-started/for-developers/v0.dev\#go-to-code-section)    Go to "Code" section

Select "Typescript" in the "Language", and copy the code.

Instruct v0.dev to use a Next.js serverless function to expose the WorkflowAI agent as a API route. Because integration WorkflowAI SDK on the front-end will be a security risk, you don't want your API key to be exposed to the client.

3

#### [Direct link to heading](https://docs.workflowai.com/getting-started/for-developers/v0.dev\#get-your-workflowai-api-key)    Get your WorkflowAI API key

From the "Code" section, click on "Manage Secret keys", and follow the process to create a new secret key. Make sure to copy the API key, which will be displayed only once.

4

#### [Direct link to heading](https://docs.workflowai.com/getting-started/for-developers/v0.dev\#setup-api-key-as-a-environment-variable)    Setup API key as a environment variable

Set up `WORKFLOWAI_API_KEY` as an environment variable in your v0.dev project.

Use exactly `WORKFLOWAI_API_KEY` as the environment variable name. If you need to use a different variable name, use:

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
const workflowAI = new WorkflowAI({
    key: "YOUR_API_KEY"
})
```

You can setup the environment variable as:

- [specific for the Vercel project](https://vercel.com/docs/projects/environment-variables/managing-environment-variables)

- [shared for all Vercel projects](https://vercel.com/docs/projects/environment-variables/shared-environment-variables)


Read more on [Vercel documentation](https://vercel.com/docs/projects/environment-variables)

...

## [Direct link to heading](https://docs.workflowai.com/getting-started/for-developers/v0.dev\#video)    Video

\[video\]

## [Direct link to heading](https://docs.workflowai.com/getting-started/for-developers/v0.dev\#examples)    Examples

github repo: https://github.com/workflowai/v0-dev-example

## [Direct link to heading](https://docs.workflowai.com/getting-started/for-developers/v0.dev\#help)    Help

If you have any questions, please reach out to us on [Slack](https://workflowai.com/slack).

[PreviousCursorAI Integration](https://docs.workflowai.com/getting-started/for-developers/cursor) [NextIntroduction](https://docs.workflowai.com/ai-agents-playbook/introduction)

Last updated 1 month ago

Was this helpful?

* * *