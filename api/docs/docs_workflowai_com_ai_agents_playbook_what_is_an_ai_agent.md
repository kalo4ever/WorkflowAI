> The unprecedented capabilities of foundation models have opened the door to agentic applications that were previously unimaginable. These new capabilities make it finally possible to develop autonomous, intelligent agents to act as our assistants, coworkers, and coaches. They can help us create a website, gather data, plan a trip, do market research, manage a customer account, automate data entry, prepare us for interviews, interview our candidates, negotiate a deal, etc. The possibilities seem endless, and the potential economic value of these agents is enormous. [Chip Huyen](https://huyenchip.com/2025/01/07/agents.html)

AI agents are mini-programs that use AI algorithms (LLMs) as their brain to accomplish tasks typically provided by users or other agents. The AI agent understands the task requirements, plans a sequence of actions to achieve the task, executes the actions, and determines whether the task has been successfully completed.

For example, a AI agent can:

- summarize a text \[todo: add link to public task\]

- browse a company URL to extract the list of customers \[todo: add link to public task\]

- generate SOAP notes from a medical report \[todo: add link to public task\]

- search the web to answer a question \[todo: add link to public task\]

- generate product descriptions from images \[todo: add link to public task\]

- extract structured data from a PDF, image \[todo: add link to public task\]

- classify a customer message into a category \[todo: add link to public task\]

- scrape a listing website to extract structured data \[todo: add link to public task\]

- \[add more examples, link\]


AI agents can access [tools](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent#tools), some of which are built-in, like searching the web, navigating on webpages, or your own custom tools. The success of an agent depends on both the tools available to it and the capabilities of its AI planner.

REAL-LIFE EXAMPLE [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent#real-life-example)

Apple recently introduced a AI agent that can rewrite a text with a different tone.

\[image\]

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent\#what-ai-agents-can-you-leverage)    What AI Agents can you leverage?

The easiest way to get started with a personalized list of AI agents for your product and company is to go to [workflowai.com](https://workflowai.com/) and enter your company URL.

WorkflowAI will generate a list of AI agents that are most likely to be useful for your company.

INSIDE WORKFLOWAI'S OWN AGENTS [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent#inside-workflowais-own-agents)

When you use our feature that generates a list of AI agents from a company URL, under the hood, we're using 2 agents: - a first \[agent\](https://workflowai.com/agents/1) is generating a profile of the company, by searching the web, and browsing the company website. - a second \[agent\](https://workflowai.com/agents/2) is generating a list of AI agents that are most likely to be useful for your company.

REAL-LIFE AGENT [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent#real-life-agent)

Berrystreet.co, a company that ..., developed a AI agent that can write SOAP notes from a medical report, using WorkflowAI, and deployed it to production. Since then, the agent has been used to generate over 1000 SOAP notes.

\[image\]

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent\#by-use-case)    By use case

Use Case

AI Agents

Text Generation

• Blog articles and marketing copy
• Email replies and messages
• Medical and business documentation
• Educational content and quizzes
• Personalized recommendations

Text Processing

• Multi-language translation
• Text tone and style modification
• Grammar and content optimization
• Document summarization
• Conversation and issue titling

Data Extraction

• Document and form processing
• Calendar and event extraction
• Medical and business code analysis
• Structured data extraction
• Real estate and shipping details

Analysis & Detection

• Content moderation and safety
• Threat and fraud detection
• Sentiment and style analysis
• Priority classification

Media Processing

• Image analysis and tagging
• Food and product recognition
• Video transcription and analysis
• Key moment identification

Interactive Systems

• Specialized chatbots
• Memory-enhanced conversations
• Knowledge-based Q&A

Industry Solutions

• Healthcare documentation
• Financial processing
• Real estate analysis
• E-commerce optimization
• Marketing automation

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent\#by-industry)    By industry

Industry

AI Agents

Healthcare

• SOAP notes generation from transcripts
• Medical data extraction and summarization
• Medical document translation
• Therapeutic guidance chatbots

Finance & Banking

• Fraud detection
• Loan application processing
• Financial document analysis and extraction
• Transaction verification

E-commerce & Retail

• Product categorization and tagging
• Customer feedback and sentiment analysis
• Product image analysis
• Marketing copy generation

Real Estate

• Property document analysis
• Listing details extraction and generation
• Contract analysis
• Document translation

Technology & Software

• App review and feedback analysis
• Issue management
• Content moderation
• Security vulnerability detection
• Communication assistance

Education & Learning

• Educational content generation
• Language learning tools
• Content summarization and translation
• Interactive tutoring

Marketing & Media

• Content generation and adaptation
• Multilingual content management
• Copy optimization
• Content tone modification

Logistics & Supply Chain

• Document processing and analysis
• Data extraction
• Address verification
• Document translation

Insurance

• Policy and claim analysis
• Document processing
• Coverage verification
• Document summarization

Content & Publishing

• Media accessibility tools
• Content moderation
• Language processing
• Document translation

## [Direct link to heading](https://docs.workflowai.com/ai-agents-playbook/what-is-an-ai-agent\#tools)    Tools

Let's look at why tools are so important through a simple example:

Web browsing was one of the first major tools added to ChatGPT. Without it, ChatGPT could only access information from its training data, which becomes outdated quickly. It couldn't tell you today's weather, recent news, upcoming events, or real-time stock prices. Web browsing keeps the agent current and vastly more useful.

This illustrates a key point: while an AI agent can function without external tools (like an LLM generating text), tools dramatically expand what an agent can do. Tools enable agents to perceive and interact with their environment in ways that would otherwise be impossible.

When designing an agent, carefully consider what tools to provide:

- More tools expand the agent's capabilities

- But too many tools can make it harder for the agent to be effective

- Finding the right balance requires experimentation


Common categories of tools include:

1. Knowledge augmentation tools (for building context)



- Web search to get current information

- Document retrieval from company knowledge bases

- Database queries to access structured data


2. Capability extension tools



- Image generation and analysis

- Text-to-speech and speech-to-text conversion

- Code execution and debugging

- Language translation


3. Environment interaction tools



- API calls to external services

- Web browser automation

- File system operations

- Email and messaging integrations


The tools you give an agent will determine what it can accomplish. We'll cover tool selection strategy later in the playbook.

[PreviousIntroduction](https://docs.workflowai.com/ai-agents-playbook/introduction) [NextBuilding your first AI agent](https://docs.workflowai.com/ai-agents-playbook/building-your-first-ai-agent)

Last updated 1 month ago

Was this helpful?

* * *