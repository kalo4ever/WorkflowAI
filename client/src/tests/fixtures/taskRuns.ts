import { TaskRun } from '@/types';
import { TaskSchemaResponseWithSchema } from '@/types/task';

export const taskRunFixtures: {
  taskSchema: TaskSchemaResponseWithSchema;
  taskRuns: TaskRun[];
} = {
  taskSchema: {
    name: 'TaskInputOutputClassGeneration',
    task_id: 'taskinputoutputclassgeneration',
    schema_id: 1,
    input_schema: {
      version: '91c4fa573a996bd7f8d1649a0ec34935',
      json_schema: {
        properties: {
          task_description: {
            title: 'Task Description',
            type: 'string',
          },
        },
        required: ['task_description'],
        title: 'TaskInputOutputClassGenerationTaskInput',
        type: 'object',
      },
    },
    is_hidden: false,
    output_schema: {
      version: '5dfc36368c452bdfcf5c5210b32906c7',
      json_schema: {
        properties: {
          task_name: {
            description: 'The name of the task in PascalCase',
            title: 'Task Name',
            type: 'string',
          },
          input_json_schema: {
            title: 'Input Json Schema',
            type: 'object',
          },
          output_json_schema: {
            title: 'Output Json Schema',
            type: 'object',
          },
        },
        required: ['task_name', 'input_json_schema', 'output_json_schema'],
        title: 'TaskInputOutputClassGenerationTaskOutput',
        type: 'object',
      },
    },
  },
  taskRuns: [
    {
      id: 'e0d9b5ea-1c64-481a-bdae-1ad157010a8a',
      task_id: 'taskinputoutputclassgeneration',
      task_schema_id: 1,
      task_input: {
        task_description:
          'Create a class that handles input and output operations.',
      },
      task_input_hash: '376305826d58a42181d5c2377ad7db7f',
      task_output: {
        task_name: 'TaskInputOutputClassGeneration',
        input_json_schema: {
          title: 'Task Description',
          type: 'string',
        },
        output_json_schema: {
          properties: {
            task_name: {
              description: 'The name of the task in PascalCase',
              title: 'Task Name',
              type: 'string',
            },
            input_json_schema: {
              title: 'Input Json Schema',
              type: 'object',
            },
            output_json_schema: {
              title: 'Output Json Schema',
              type: 'object',
            },
          },
          required: ['task_name', 'input_json_schema', 'output_json_schema'],
          title: 'TaskInputOutputClassGenerationTaskOutput',
          type: 'object',
        },
      },
      task_output_hash: 'a030dea47954c9c5eb1b6379d8b51dde',
      group: {
        // id: '0f71e53ad05cc09c44a018f163ada523',
        iteration: 2,
        properties: {
          model: 'gpt-3.5-turbo-1106',
          provider: 'openai',
          name: 'WorkflowAI',
          runner_name: 'WorkflowAI',
          runner_version: '193c996bb972aba3d50a62905b80ab14',
          variant_id: '0f71e53ad05cc09c44a018f163ada523',
        },
        tags: [
          'model=gpt-3.5-turbo-1106',
          'name=WorkflowAI',
          'provider=openai',
        ],
      },
      start_time: '2024-04-24T14:10:39.883000Z',
      end_time: '2024-04-24T14:10:43.125000Z',
      duration_seconds: 3.241879,
      created_at: '2024-04-24T15:58:03.551754',
      example_id: null,
      corrections: null,
    },
    {
      id: '05a43b59-5ca1-4237-964e-89280e756e6a',
      task_id: 'taskinputoutputclassgeneration',
      task_schema_id: 1,
      task_input: {
        task_description: 'Create an text based on an emotion',
      },
      task_input_hash: '16b26e29d58ec31cd3769fc559f3127f',
      task_output: {
        task_name: 'GenerateTextFromEmotion',
        input_json_schema: {
          type: 'object',
          properties: {
            emotion: {
              type: 'string',
              description: 'The emotion to base the text on',
              examples: ['happiness', 'sadness', 'anger'],
            },
          },
          required: ['emotion'],
        },
        output_json_schema: {
          type: 'object',
          properties: {
            generated_text: {
              type: 'string',
              description: 'The text generated based on the specified emotion',
              examples: [
                'I feel a surge of joy and contentment.',
                'A deep sorrow shadows my heart.',
                'Fury burns within me, unquenchable and fierce.',
              ],
            },
          },
          required: ['generated_text'],
        },
      },
      task_output_hash: '9e0242b1b800f4f7f067a1e4fdd44dc8',
      group: {
        // id: 'fb97dfd441f27ac612329688f8c3fe0a',
        iteration: 1,
        properties: {
          model: 'gpt-4-turbo-2024-04-09',
          provider: 'openai',
          temperature: 0,
          name: 'WorkflowAI',
          runner_name: 'WorkflowAI',
          runner_version: 'abd8fc3062851e549447b9805362d229',
          variant_id: '0f71e53ad05cc09c44a018f163ada523',
        },
        tags: [
          'model=gpt-4-turbo-2024-04-09',
          'name=WorkflowAI',
          'provider=openai',
          'temperature=0.00',
        ],
      },
      start_time: '2024-04-24T14:19:13.165000Z',
      end_time: '2024-04-24T14:19:24.402000Z',
      duration_seconds: 11.236597,
      created_at: '2024-04-24T15:58:03.551754',
      example_id: null,
      corrections: null,
    },
    {
      id: 'e5f29e9b-f867-42ba-b7ea-de9489bd23f4',
      task_id: 'taskinputoutputclassgeneration',
      task_schema_id: 1,
      task_input: {
        task_description: 'hello world',
      },
      task_input_hash: '6eb0ecdbbdafa2470c6bb3cf0bb2afd0',
      task_output: {
        task_name: 'HelloWorld',
        input_json_schema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'A simple greeting message to display',
              example: 'Hello, world!',
            },
          },
          required: ['message'],
        },
        output_json_schema: {
          type: 'object',
          properties: {
            response: {
              type: 'string',
              description:
                'The response message echoing the input with acknowledgment',
              example: 'Received your message: Hello, world!',
            },
          },
          required: ['response'],
        },
      },
      task_output_hash: '6f7719e236127e275a4bce4d37ce92f5',
      group: {
        // id: 'fb97dfd441f27ac612329688f8c3fe0a',
        iteration: 1,
        properties: {
          model: 'gpt-4-turbo-2024-04-09',
          provider: 'openai',
          temperature: 0,
          name: 'WorkflowAI',
          runner_name: 'WorkflowAI',
          runner_version: 'abd8fc3062851e549447b9805362d229',
          variant_id: '0f71e53ad05cc09c44a018f163ada523',
        },
        tags: [
          'model=gpt-4-turbo-2024-04-09',
          'name=WorkflowAI',
          'provider=openai',
          'temperature=0.00',
        ],
      },
      start_time: '2024-04-24T14:21:18.848000Z',
      end_time: '2024-04-24T14:21:26.351000Z',
      duration_seconds: 7.502245,
      created_at: '2024-04-24T15:58:03.551754',
      example_id: null,
      corrections: null,
    },
    {
      id: '9cc3825f-77eb-41e8-88e4-d924fea6afa7',
      task_id: 'taskinputoutputclassgeneration',
      task_schema_id: 1,
      task_input: {
        task_description: 'coucou',
      },
      task_input_hash: '3173699df2331186e8e81a60affe5223',
      task_output: {
        task_name: 'Coucou',
        input_json_schema: {
          properties: {
            greeting: {
              type: 'string',
              description: 'A simple greeting or salutation',
              examples: ['Hello', 'Hi', 'Coucou'],
            },
          },
          required: ['greeting'],
          type: 'object',
        },
        output_json_schema: {
          properties: {
            response: {
              type: 'string',
              description: 'A friendly response to the greeting',
              examples: [
                'Hello there!',
                'Hi, how can I help you?',
                'Coucou! How are you?',
              ],
            },
          },
          required: ['response'],
          type: 'object',
        },
      },
      task_output_hash: 'b07c2ad7c6ab1d2cd5a2d4d41101618b',
      group: {
        // id: 'fb97dfd441f27ac612329688f8c3fe0a',
        iteration: 1,
        properties: {
          model: 'gpt-4-turbo-2024-04-09',
          provider: 'openai',
          temperature: 0,
          name: 'WorkflowAI',
          runner_name: 'WorkflowAI',
          runner_version: 'abd8fc3062851e549447b9805362d229',
          variant_id: '0f71e53ad05cc09c44a018f163ada523',
        },
        tags: [
          'model=gpt-4-turbo-2024-04-09',
          'name=WorkflowAI',
          'provider=openai',
          'temperature=0.00',
        ],
      },
      start_time: '2024-04-24T14:40:36.078000Z',
      end_time: '2024-04-24T14:40:47.910000Z',
      duration_seconds: 11.832028,
      created_at: '2024-04-24T15:58:03.551754',
      example_id: null,
      corrections: null,
    },
    {
      id: '0e90f079-b1d5-4b34-b149-e73a0fc3bd74',
      task_id: 'taskinputoutputclassgeneration',
      task_schema_id: 1,
      task_input: {
        task_description: 'hello world',
      },
      task_input_hash: '6eb0ecdbbdafa2470c6bb3cf0bb2afd0',
      task_output: {
        task_name: 'HelloWorld',
        input_json_schema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'A simple greeting message',
              example: 'Hello, world!',
            },
          },
          required: ['message'],
        },
        output_json_schema: {
          type: 'object',
          properties: {
            response: {
              type: 'string',
              description: 'A response to the greeting message',
              example: 'Hi there!',
            },
          },
          required: ['response'],
        },
      },
      task_output_hash: '34e8bb0b4c843c36f430e69217f52545',
      group: {
        // id: 'fb97dfd441f27ac612329688f8c3fe0a',
        iteration: 1,
        properties: {
          model: 'gpt-4-turbo-2024-04-09',
          provider: 'openai',
          temperature: 0,
          name: 'WorkflowAI',
          runner_name: 'WorkflowAI',
          runner_version: 'abd8fc3062851e549447b9805362d229',
          variant_id: '0f71e53ad05cc09c44a018f163ada523',
        },
        tags: [
          'model=gpt-4-turbo-2024-04-09',
          'name=WorkflowAI',
          'provider=openai',
          'temperature=0.00',
        ],
      },
      start_time: '2024-04-24T09:16:41.431000Z',
      end_time: '2024-04-24T09:16:51.347000Z',
      duration_seconds: 9.915893,
      created_at: '2024-04-24T15:58:03.551754',
      example_id: null,
      corrections: null,
    },
    {
      id: '07d84ffa-3ba7-4a32-9a8b-d70a41694428',
      task_id: 'taskinputoutputclassgeneration',
      task_schema_id: 1,
      task_input: {
        task_description: 'Hello world',
      },
      task_input_hash: '85be0a3405d0ba3e94fa3978fce56155',
      task_output: {
        task_name: 'HelloWorld',
        input_json_schema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'A simple greeting message',
              example: 'Hello, world!',
            },
          },
          required: ['message'],
        },
        output_json_schema: {
          type: 'object',
          properties: {
            response: {
              type: 'string',
              description: 'The response to the greeting message',
              example: 'Hello to you too!',
            },
          },
          required: ['response'],
        },
      },
      task_output_hash: 'af4caa0f31506cd009773530e3769d98',
      group: {
        // id: 'fb97dfd441f27ac612329688f8c3fe0a',
        iteration: 1,
        properties: {
          model: 'gpt-4-turbo-2024-04-09',
          provider: 'openai',
          temperature: 0,
          name: 'WorkflowAI',
          runner_name: 'WorkflowAI',
          runner_version: 'abd8fc3062851e549447b9805362d229',
          variant_id: '0f71e53ad05cc09c44a018f163ada523',
        },
        tags: [
          'model=gpt-4-turbo-2024-04-09',
          'name=WorkflowAI',
          'provider=openai',
          'temperature=0.00',
        ],
      },
      start_time: '2024-04-24T09:18:46.116000Z',
      end_time: '2024-04-24T09:18:54.522000Z',
      duration_seconds: 8.405886,
      created_at: '2024-04-24T15:58:03.551754',
      example_id: null,
      corrections: null,
    },
  ],
};
