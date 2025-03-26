## [Direct link to heading](https://docs.workflowai.com/concepts/versions\#what-is-a-version)    What is a version?

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

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-dd71ee668a040738cd565059520b3f262e161694%252Fversions.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=fc312f40&sv=2)

Version 2 is a major version, version 2.1 is version 2 running on Gemini 2.0

## [Direct link to heading](https://docs.workflowai.com/concepts/versions\#why-are-versions-useful)    Why are versions useful?

Versions are useful for several reasons:

- They allow you to save a specific configuration of an agent, so you can reproduce it later.

- They allow you to [compare the performance of different versions of an agent](https://docs.workflowai.com/ai-agents-playbook/evaluating-your-ai-agent).

- They allow you to [deploy a specific version of an agent](https://docs.workflowai.com/features/deployments).


## [Direct link to heading](https://docs.workflowai.com/concepts/versions\#how-to)    How to:

### [Direct link to heading](https://docs.workflowai.com/concepts/versions\#save-a-version)    Save a version

When using the playground, you can save a version by clicking on the "Save" button.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-feb4d4bef0467b8d7bc262618d101c0ef9e6bd8e%252Fsave-version.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=de5bfeb8&sv=2)

Save a version

Additionnaly, you can save all versions currently running by clicking on the "Save all versions" button.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-532117833f3902d81ded6dd642e61d96dd2b0796%252Fsave-all-versions.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=61b26c08&sv=2)

Save all versions

You should save a version when you're satisfied with the LLM output and want to preserve the current configuration. A saved version captures your chosen model, prompt, temperature setting, and other parameters, allowing you to reliably reproduce these results later, or use them in a [deployment](https://github.com/WorkflowAI/documentation/blob/main/deployments/README.md).

### [Direct link to heading](https://docs.workflowai.com/concepts/versions\#list-all-versions)    List all versions

You can access the list of all versions by clicking on the "Versions" section from the menu.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-db9ad237eaff4b24e0c07b7db0b9afc966f2d399%252Fversions-section-full.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=61276601&sv=2)

List of all versions

### [Direct link to heading](https://docs.workflowai.com/concepts/versions\#clone-a-version)    Clone a version

Cloning a version is useful when you want to create a new version based on an existing version. For example, you have a version running on OpenAI's GPT-4o-mini, and you want to quickly reuse the same instructions, temperature, and tools for a new version running on Gemini 2.0.

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2FWorkflowAI%2Fdocumentation%2Fblob%2Fmain%2Fdocs%2Fassets%2Fimages%2Fversions%2Fclone-version.gif&width=768&dpr=4&quality=100&sign=e3758f28&sv=2)

Clone a version

[PreviousSchemas](https://docs.workflowai.com/concepts/schemas) [NextRuns](https://docs.workflowai.com/concepts/runs)

Last updated 10 days ago

Was this helpful?

* * *