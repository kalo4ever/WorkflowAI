import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonObjectSchema } from '@/types';
import { SchemaEditorTextCaseFixture } from './types';

const originalSchema: JsonObjectSchema = {
  type: 'object',
  properties: {
    name: {
      type: 'string',
      description: 'Name of the person',
      default: 'John Doe',
    },
    age: {
      type: 'integer',
      examples: [20, 21, 22],
    },
    weight: {
      type: 'number',
      examples: [60.5, 61.5, 62.5],
    },
    isStudent: {
      type: 'boolean',
      title: 'Is Student',
    },
    birthDateTime: {
      type: 'string',
      format: 'date-time',
    },
    birthDate: {
      type: 'string',
      format: 'date',
    },
    birthTimezone: {
      type: 'string',
      format: 'timezone',
    },
    birthTime: {
      type: 'string',
      format: 'time',
    },
    gender: {
      type: 'string',
      enum: ['Male', 'Female', 'Other'],
    },
    genders: {
      type: 'array',
      items: {
        type: 'string',
        enum: ['Male', 'Female', 'Other'],
      },
    },
    isAdmin: {
      type: 'boolean',
      default: false,
    },
    htmlSample: {
      type: 'string',
      format: 'html',
    },
    grades: {
      type: 'array',
      items: {
        type: 'integer',
        examples: [80, 90, 100],
      },
    },
    favoriteMovie: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
        },
        description: {
          type: 'string',
        },
        director: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
            },
            age: {
              type: 'integer',
            },
          },
        },
      },
    },
    projects: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
          },
          description: {
            type: 'string',
          },
          tasks: {
            type: 'array',
            items: {
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
          },
        },
      },
    },
  },
};

const splattedEditorFields: SchemaEditorField = {
  keyName: '',
  type: 'object',
  fields: [
    {
      keyName: 'name',
      type: 'string',
      description: 'Name of the person',
      default: 'John Doe',
    },
    {
      keyName: 'age',
      type: 'integer',
      examples: [20, 21, 22],
    },
    {
      keyName: 'weight',
      type: 'number',
      examples: [60.5, 61.5, 62.5],
    },
    {
      keyName: 'isStudent',
      type: 'boolean',
      title: 'Is Student',
    },
    {
      keyName: 'birthDateTime',
      type: 'date-time',
    },
    {
      keyName: 'birthDate',
      type: 'date',
    },
    {
      keyName: 'birthTimezone',
      type: 'timezone',
    },
    {
      keyName: 'birthTime',
      type: 'time',
    },
    {
      keyName: 'gender',
      type: 'enum',
      enum: ['Male', 'Female', 'Other'],
    },
    {
      keyName: 'genders',
      type: 'array',
      arrayType: 'enum',
      fields: [
        {
          keyName: 'genders',
          type: 'enum',
          enum: ['Male', 'Female', 'Other'],
        },
      ],
    },
    {
      keyName: 'isAdmin',
      type: 'boolean',
      default: false,
    },
    {
      keyName: 'htmlSample',
      type: 'html',
    },
    {
      keyName: 'grades',
      type: 'array',
      arrayType: 'integer',
      fields: [
        {
          keyName: 'grades',
          type: 'integer',
          examples: [80, 90, 100],
        },
      ],
    },
    {
      keyName: 'favoriteMovie',
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
        {
          keyName: 'director',
          type: 'object',
          fields: [
            {
              keyName: 'name',
              type: 'string',
            },
            {
              keyName: 'age',
              type: 'integer',
            },
          ],
        },
      ],
    },
    {
      keyName: 'projects',
      type: 'array',
      arrayType: 'object',
      fields: [
        {
          keyName: 'name',
          type: 'string',
        },
        {
          keyName: 'description',
          type: 'string',
        },
        {
          keyName: 'tasks',
          type: 'array',
          arrayType: 'object',
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
      ],
    },
  ],
};

export const simpleObjectSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema: originalSchema,
};
