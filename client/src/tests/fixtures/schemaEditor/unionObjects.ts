import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonObjectSchema } from '@/types';
import { SchemaEditorTextCaseFixture } from './types';

const originalSchema: JsonObjectSchema = {
  type: 'object',
  properties: {
    passion: {
      anyOf: [
        {
          type: 'string',
        },
        {
          type: 'object',
          properties: {
            name: {
              type: 'string',
            },
            description: {
              type: 'string',
            },
          },
        },
      ],
    },
    dream: {
      oneOf: [
        {
          type: 'object',
          properties: {
            name: {
              type: 'string',
            },
            description: {
              type: 'string',
            },
          },
        },
        {
          type: 'string',
        },
        {
          type: 'null',
        },
      ],
    },
    fear: {
      allOf: [
        {
          type: 'null',
        },
        {
          type: 'string',
          examples: ['spiders', 'heights', 'failure'],
        },
      ],
    },
  },
};

const splattedEditorFields: SchemaEditorField = {
  keyName: '',
  type: 'object',
  fields: [
    {
      keyName: 'passion',
      type: 'string',
    },
    {
      keyName: 'dream',
      type: 'object',
      fields: [
        {
          keyName: 'name',
          type: 'string',
        },
        {
          keyName: 'description',
          type: 'string',
        },
      ],
    },
    {
      keyName: 'fear',
      type: 'string',
      examples: ['spiders', 'heights', 'failure'],
    },
  ],
};

const finalSchema: JsonObjectSchema = {
  type: 'object',
  properties: {
    passion: {
      type: 'string',
    },
    dream: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
        },
        description: {
          type: 'string',
        },
      },
    },
    fear: {
      type: 'string',
      examples: ['spiders', 'heights', 'failure'],
    },
  },
};

export const unionObjectsSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema,
};
