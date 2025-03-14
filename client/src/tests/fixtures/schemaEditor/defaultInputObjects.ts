import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonObjectSchema } from '@/types';
import { SchemaEditorTextCaseFixture } from './types';

const originalSchema: JsonObjectSchema = {
  type: 'object',
  properties: {
    firstName: {
      type: 'string',
      description: 'First name',
    },
    lastName: {
      type: 'string',
      description: 'Last name',
    },
  },
};

const splattedEditorFields: SchemaEditorField = {
  keyName: '',
  type: 'object',
  fields: [
    {
      keyName: 'firstName',
      type: 'string',
      description: 'First name',
    },
    {
      keyName: 'lastName',
      type: 'string',
      description: 'Last name',
    },
  ],
};

export const defaultInputObjectSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema: originalSchema,
};
