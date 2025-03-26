## [Direct link to heading](https://docs.workflowai.com/concepts/schemas\#what-are-schemas)    What are schemas?

An AI agent has at least one schema. Each schema define:

- an input structure

- an output structure


For example, a [task that answer question about a PDF](https://workflowai.dev/workflowai/tasks/pdf-question-answering/1/schemas) is represented:

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-9f7940c1402e6d276946dce951eb166b3fa777c7%252Fschema.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=28d80256&sv=2)

alt text

PythonTypeScript

WorkflowAI uses [Pydantic](https://docs.pydantic.dev/) to define schemas.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
class PdfQuestionAnsweringTaskInput(BaseModel):
    pdf_document: Optional[File] = None
    question: Optional[str] = None

class SupportingQuote(BaseModel):
    quote: Optional[str] = None
    page_number: Optional[float] = None

class PdfQuestionAnsweringTaskOutput(BaseModel):
    answer: Optional[str] = None
    supporting_quotes: Optional[list[SupportingQuote]] = None
```

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
interface PdfQuestionAnsweringTaskInput {
    pdf_document?: File;
    question?: string;
}

interface SupportingQuote {
    quote?: string;
    page_number?: number;
}

interface PdfQuestionAnsweringTaskOutput {
    answer?: string;
    supporting_quotes?: SupportingQuote[];
}
```

## [Direct link to heading](https://docs.workflowai.com/concepts/schemas\#examples)    Examples

For example, if you want an agent to summarize a text, the input is a text, and the output is a summary. If you want this agent to summarize a text in a specific language, you'll need to add a language parameter to the input. The inputs are like all the variables the LLM will have access to. The outputs are the different variables the LLM will generate.

When using WorkflowAI web-app, you can write what you want the agent to do, and the web-app will generate a schema for you.

## [Direct link to heading](https://docs.workflowai.com/concepts/schemas\#why-are-schemas-a-good-idea)    Why are schemas a good idea?

Clear input and output structures (=schemas) have a few benefits:

1. simplify integration with a backend by providing a clear interface

2. provide output consistency

3. increase the quality of LLM outputs by structuring the task


### [Direct link to heading](https://docs.workflowai.com/concepts/schemas\#technical-details)    Technical details

WorkflowAI leverages structured generation, also called [structured output](https://platform.openai.com/docs/guides/structured-outputs), or [controlled generation](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output). Structured generation is currently enabled for [all supported OpenAI models](https://platform.openai.com/docs/guides/structured-outputs), and for all models on [Fireworks](https://docs.fireworks.ai/structured-responses/structured-response-formatting#structured-response-modes). When structured generation is not available, WorkflowAI automatically falls back to [JSON mode](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/increase-consistency), and **always guarantees** the output will follow the output schema.

## [Direct link to heading](https://docs.workflowai.com/concepts/schemas\#how-to-create-a-schema)    How to create a schema?

WorkflowAI supports two ways to create a task schema:

- using our web-app, using AI or manually.

- using code, via Cursor.


\[video\]

## [Direct link to heading](https://docs.workflowai.com/concepts/schemas\#edit-a-schema)    Edit a schema

Finding the right schema takes a few iterations, so we try to make editing a schema as easy as possible.

\[video\]

When possible, we recommend to edit the schema using the chat. If you need more control, you can manually edit the schema.

## [Direct link to heading](https://docs.workflowai.com/concepts/schemas\#archiving-a-schema)    Archiving a schema

When building a new task, it's very likely you'll need multiple iterations to get the right schema. To clean up unused schemas, you can archive them.

To archive a schema, navigate to the "Schemas" section from the menu, and click on the "Archive" button in the schema's detail view.

!\[alt text\](assets/Screenshot 2025-01-03 at 16.04.38.png) \[video\]

Archived schemas are not deleted, but hidden from the UI. Any deployment or version using an archived schema will continue to work, to avoid breaking changes.

[PreviousAI Agents](https://docs.workflowai.com/concepts/ai-agents) [NextVersions](https://docs.workflowai.com/concepts/versions)

Last updated 1 month ago

Was this helpful?

* * *