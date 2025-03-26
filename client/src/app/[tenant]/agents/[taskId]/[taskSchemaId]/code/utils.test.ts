import { JsonSchema, JsonSchemaDefinitions } from '@/types';
import { JPG_SAMPLE_URL, MP3_SAMPLE_URL, generateInputsForCodeGeneration } from './utils';

const $defs: JsonSchemaDefinitions = {
  Image: {
    type: 'object',
    properties: {
      url: {
        type: 'string',
      },
    },
  },
};

describe('generateInputsForCodeGeneration', () => {
  it('should replace file data with URL', () => {
    const schema: JsonSchema = {
      $defs,
      type: 'object',
      properties: {
        image: {
          $ref: '#/$defs/Image',
        },
      },
    };

    const task_input = {
      image: {
        data: 'sample',
        content_type: 'image/jpeg',
      },
    };

    const [result, secondaryInput] = generateInputsForCodeGeneration(
      // @ts-expect-error we only need to input here
      [{ task_input }],
      schema
    );

    expect(result?.task_input).toEqual({
      image: {
        url: JPG_SAMPLE_URL,
      },
    });
    expect(secondaryInput).toEqual({
      image: {
        data: 'sample',
        content_type: 'image/jpeg',
      },
    });
  });

  it('should replace file data with URL for audio', () => {
    const schema: JsonSchema = {
      $defs,
      type: 'object',
      properties: {
        audio: {
          $ref: '#/$defs/Image',
          format: 'audio',
        },
      },
    };

    const task_input = {
      audio: {
        data: 'sample',
        content_type: 'audio/mpeg',
        name: 'sample.mp3',
      },
    };

    const [result, secondaryInput] = generateInputsForCodeGeneration(
      // @ts-expect-error we only need to input here
      [{ task_input }],
      schema
    );

    expect(result?.task_input).toEqual({
      audio: {
        url: MP3_SAMPLE_URL,
      },
    });
    expect(secondaryInput).toEqual({
      audio: {
        data: 'sample',
        content_type: 'audio/mpeg',
      },
    });
  });

  it('should return the original object if it is not a file', () => {
    const schema: JsonSchema = {
      type: 'object',
      properties: {
        text: {
          type: 'string',
        },
      },
    };

    const task_input = {
      text: 'sample',
    };

    const [result, secondaryInput] = generateInputsForCodeGeneration(
      // @ts-expect-error we only need to input here
      [{ task_input }],
      schema
    );

    expect(result?.task_input).toEqual(task_input);
    expect(secondaryInput).toBe(undefined);
  });

  it('should not replace url if url is not schema', () => {
    const schema: JsonSchema = {
      $defs: {
        Image: {
          type: 'object',
          properties: {
            data: {
              type: 'string',
            },
          },
        },
      },
      type: 'object',
      properties: {
        image: {
          $ref: '#/$defs/Image',
        },
      },
    };

    const task_input = {
      image: {
        data: 'sample',
        content_type: 'image/jpeg',
      },
    };

    const [result, secondaryInput] = generateInputsForCodeGeneration(
      // @ts-expect-error we only need to input here
      [{ task_input }],
      schema
    );

    expect(result?.task_input).toEqual(task_input);
    expect(secondaryInput).toBe(undefined);
  });

  it('should work with image arrays', () => {
    const schema: JsonSchema = {
      $defs,
      type: 'object',
      properties: {
        images: {
          type: 'array',
          items: {
            $ref: '#/$defs/Image',
          },
        },
      },
    };
    const task_input = {
      images: [
        {
          data: 'sample',
          content_type: 'image/jpeg',
        },
        {
          data: 'sample1',
          content_type: 'image/jpeg',
        },
      ],
    };

    const [result, secondaryInput] = generateInputsForCodeGeneration(
      // @ts-expect-error we only need to input here
      [{ task_input }],
      schema
    );

    expect(result?.task_input).toEqual({
      images: [
        {
          url: JPG_SAMPLE_URL,
        },
        {
          url: JPG_SAMPLE_URL,
        },
      ],
    });
    expect(secondaryInput).toEqual({
      images: [
        {
          data: 'sample',
          content_type: 'image/jpeg',
        },
        {
          data: 'sample1',
          content_type: 'image/jpeg',
        },
      ],
    });
  });

  it('should replace in deep objects', () => {
    const schema: JsonSchema = {
      $defs,
      type: 'object',
      properties: {
        another: {
          type: 'object',
          properties: {
            image: {
              $ref: '#/$defs/Image',
            },
          },
        },
      },
    };

    const task_input = {
      another: {
        image: {
          data: 'sample',
          content_type: 'image/jpeg',
        },
      },
    };

    const [result, secondaryInput] = generateInputsForCodeGeneration(
      // @ts-expect-error we only need to input here
      [{ task_input }],
      schema
    );

    expect(result?.task_input).toEqual({
      another: {
        image: {
          url: JPG_SAMPLE_URL,
        },
      },
    });
    expect(secondaryInput).toEqual({
      another: {
        image: {
          data: 'sample',
          content_type: 'image/jpeg',
        },
      },
    });
  });

  it('should not crash when we have freeform objects', () => {
    const task_input = {
      task_output_schema: {
        type: 'object',
        properties: {
          answer: {
            description: 'The answer to the question',
            type: 'string',
          },
        },
      },
      task_instructions: 'DO NOT THINK STEP BY STEP PLEASE PLEASE.',
    };

    const input_schema: JsonSchema = {
      type: 'object',
      properties: {
        task_output_schema: {
          description: 'A simple dictionary field',
          type: 'object',
          properties: {},
        },
        task_instructions: {
          description: 'The instructions for the AI agent to analyze',
          type: 'string',
        },
      },
    };

    generateInputsForCodeGeneration(
      // @ts-expect-error we only need to input here
      [{ task_input }],
      input_schema
    );
  });
});
