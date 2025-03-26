This feature is only available via the Python SDK for now.

## [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#what-is-prompt)    What is `@prompt`?

`@prompt` allows you to write a prompt fully customizable, using code, and still benefit from the WorkflowAI platform.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
@prompt(name='answer_question', model='gpt-4o-mini')
def prompt(question: str) -> str:
    system("You are a helpful assistant that can answer questions about the world.")
    user(question)
```

## [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#when-to-use-prompt-vs-agent)    When to use `@prompt` vs `@agent`?

For most cases, you should use `@agent` instead of `@prompt`. `@prompt` is useful when you want to write a prompt fully customizable, using code, and still benefit from the WorkflowAI platform.

## [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#tools)    Tools

## [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#structured-output)    Structured output

## [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#supported-features)    Supported features

### [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#playground)    Playground

Supported, but instructions should be left empty.

### [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#versions)    Versions

Currently not supported for `@prompt`.

### [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#benchmarks)    Benchmarks

Currently not supported for `@prompt`.

### [Direct link to heading](https://docs.workflowai.com/concepts/prompt\#deployments)    Deployments

Currently not supported for `@prompt`.

[PreviousTools](https://docs.workflowai.com/concepts/tools) [NextPlayground](https://docs.workflowai.com/features/playground)

Last updated 1 month ago

Was this helpful?

* * *