import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonObjectSchema } from '@/types';
import { SchemaEditorTextCaseFixture } from './types';

const originalSchema: JsonObjectSchema = {
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
  ],
};

const finalSchema: JsonObjectSchema = {
  type: 'object',
  ...originalSchema,
};

export const untypedObjectSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema,
};
