import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonObjectSchema, JsonSchemaDefinitions } from '@/types';
import { SchemaEditorTextCaseFixture } from './types';

const unionObjectsOriginalDefinitions: JsonSchemaDefinitions = {
  Image: {
    properties: {
      name: {
        description: 'An optional name for the image',
        title: 'Name',
        type: 'string',
      },
      content_type: {
        description: 'The content type of the image',
        examples: ['image/png', 'image/jpeg'],
        title: 'Content Type',
        type: 'string',
      },
      data: {
        description: 'The base64 encoded data of the image',
        title: 'Data',
        type: 'string',
      },
    },
    required: ['name', 'content_type', 'data'],
    title: 'Image',
    type: 'object',
  },
};

const originalSchema: JsonObjectSchema = {
  type: 'object',
  properties: {
    IMAGES: {
      type: 'array',
      items: {
        $ref: '#/$defs/Image',
      },
      description:
        'A list of input images from which to extract city and country information',
    },
  },
};

const splattedEditorFields: SchemaEditorField = {
  keyName: '',
  type: 'object',
  fields: [
    {
      keyName: 'IMAGES',
      type: 'array',
      arrayType: 'image',
      fields: undefined,
      description:
        'A list of input images from which to extract city and country information',
    },
  ],
};

export const refArrayObjectsSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema: originalSchema,
};

export const refArrayObjectDefinitionFixtures = {
  originalDefinitions: unionObjectsOriginalDefinitions,
  finalDefinitions: {},
};
