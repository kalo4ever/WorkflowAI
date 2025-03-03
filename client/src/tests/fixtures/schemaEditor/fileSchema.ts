import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonObjectSchema, JsonSchemaDefinitions } from '@/types';
import { SchemaEditorTextCaseFixture } from './types';

const definitions: JsonSchemaDefinitions = {
  File: {
    properties: {
      content_type: {
        anyOf: [
          {
            type: 'string',
          },
          {
            type: 'null',
          },
        ],
        default: null,
        description: 'The content type of the file',
        title: 'Content Type',
      },
      data: {
        anyOf: [
          {
            type: 'string',
          },
          {
            type: 'null',
          },
        ],
        default: null,
        description: 'The base64 encoded data of the file',
        title: 'Data',
      },
      url: {
        anyOf: [
          {
            type: 'string',
          },
          {
            type: 'null',
          },
        ],
        default: null,
        description: 'The URL of the image',
        title: 'Url',
      },
    },
    title: 'File',
    type: 'object',
  },
};

const originalSchema: JsonObjectSchema = {
  type: 'object',
  properties: {
    pdf_file: {
      $ref: '#/$defs/File',
      format: 'document',
    },
    txt_file: {
      $ref: '#/$defs/File',
      format: 'document',
    },
    audio_file: {
      $ref: '#/$defs/File',
      format: 'audio',
    },
    image_file: {
      $ref: '#/$defs/File',
      format: 'image',
    },
  },
};

const splattedEditorFields: SchemaEditorField = {
  keyName: '',
  type: 'object',
  fields: [
    {
      keyName: 'pdf_file',
      type: 'document',
    },
    {
      keyName: 'txt_file',
      type: 'document',
    },
    {
      keyName: 'audio_file',
      type: 'audio',
    },
    {
      keyName: 'image_file',
      type: 'image',
    },
  ],
};

const finalSchema: JsonObjectSchema = {
  type: 'object',
  properties: {
    pdf_file: {
      $ref: '#/$defs/File',
      format: 'document',
    },
    txt_file: {
      $ref: '#/$defs/File',
      format: 'document',
    },
    audio_file: {
      $ref: '#/$defs/File',
      format: 'audio',
    },
    image_file: {
      $ref: '#/$defs/Image',
    },
  },
};

export const fileSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema,
};

export const fileSchemaDefinitionFixtures = {
  originalDefinitions: definitions,
  finalDefinitions: {},
};
