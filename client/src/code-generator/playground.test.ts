import { JsonSchema } from '@/types';
import { getPlaygroundSnippets } from './playground';

const mockConfig = {
  taskId: 'test-task-123',
  taskName: 'Test Task',
  schema: {
    id: 456,
    input: {
      type: 'object',
      properties: {
        message: { type: 'string' },
      },
    } as JsonSchema,
    output: {
      type: 'object',
      properties: {
        response: { type: 'string' },
      },
    } as JsonSchema,
  },
  version: 1,
  example: {
    input: { message: 'Hello' },
    output: { response: 'World' },
  },
  api: {
    url: 'https://api.example.com',
  },
};

describe('getPlaygroundSnippets', () => {
  it('should generate all code snippets', async () => {
    const result = await getPlaygroundSnippets(mockConfig);

    expect(result).toHaveProperty('installSdk');
    expect(result).toHaveProperty('initializeClient');
    expect(result).toHaveProperty('initializeTask');
    expect(result).toHaveProperty('runTask');
    expect(result).toHaveProperty('streamRunTask');
  });

  it('should generate correct install SDK snippet', async () => {
    const { installSdk } = await getPlaygroundSnippets(mockConfig);

    expect(installSdk.language).toBe('bash');
    expect(installSdk.code).toContain('npm install @workflowai/workflowai');
    expect(installSdk.code).toContain('yarn add @workflowai/workflowai');
  });

  it('should generate initialize client without API URL when not provided', async () => {
    const configWithoutUrl = {
      ...mockConfig,
      api: { url: undefined },
    };

    const { initializeClient } = await getPlaygroundSnippets(configWithoutUrl);

    expect(initializeClient.code).not.toContain('url:');
    expect(initializeClient.code).toBe(
      `import { WorkflowAI } from "@workflowai/workflowai"

const workflowAI = new WorkflowAI({
    // optional, defaults to process.env.WORKFLOWAI_API_KEY
    // key: // Add your API key here
  })`
    );
  });

  it('should generate task code with correct types and function name', async () => {
    const { initializeTask } = await getPlaygroundSnippets(mockConfig);

    expect(initializeTask.language).toBe('typescript');
    expect(initializeTask.code).toBe(
      `export interface TestTaskInput {
  message ? : string
}

export interface TestTaskOutput {
  response ? : string
}


const testTask = workflowAI.agent < TestTaskInput, TestTaskOutput > ({
  id: "test-task-123",
  schemaId: 456,
  version: 1,
  // Cache options:
  // - "auto" (default): if a previous run exists with the same version and input, and if
  // the temperature is 0, the cached output is returned
  // - "always": the cached output is returned when available, regardless
  // of the temperature value
  // - "never": the cache is never used
  useCache: "auto"
})`
    );
  });
});

// Test the helper functions
describe('Validate variable names', () => {
  // You might need to export these functions to test them directly
  // Alternative: test them through the main function's output

  it('should generate valid variable names from task names', async () => {
    const configs = [
      { taskName: 'Test Task 123', expected: 'testTask123' },
      { taskName: 'test-task-123', expected: 'testTask123' },
      { taskName: '123test', expected: 'test' },
    ];

    for (const config of configs) {
      const result = await getPlaygroundSnippets({
        ...mockConfig,
        taskName: config.taskName,
      });
      expect(result.runTask.code).toContain(`function ${config.expected}Run()`);
      const nameExpected = config.expected.charAt(0).toUpperCase() + config.expected.slice(1);
      expect(result.initializeTask.code).toContain(
        `const ${config.expected} = workflowAI.agent < ${nameExpected}Input, ${nameExpected}Output > ({`
      );
    }
  });
});
