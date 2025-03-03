import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonObjectSchema } from '@/types';
import { SchemaEditorTextCaseFixture } from './types';

const originalSchema: JsonObjectSchema = {
  type: 'object',
  properties: {
    gender: {
      type: 'string',
      enum: ['Male', 'Female', 'Other'],
    },
  },
};

const splattedEditorFields: SchemaEditorField = {
  keyName: '',
  type: 'object',
  fields: [
    {
      keyName: 'gender',
      type: 'enum',
      enum: ['Male', 'Female', 'Other'],
    },
  ],
};

export const defaultOutputObjectSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema: originalSchema,
};
