import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonArraySchema } from '@/types';
import { simpleObjectSchemaFixture } from './simpleObject';
import { SchemaEditorTextCaseFixture } from './types';

const originalSchema: JsonArraySchema = {
  type: 'array',
  items: simpleObjectSchemaFixture.originalSchema,
};

const splattedEditorFields: SchemaEditorField = {
  keyName: '',
  type: 'array',
  arrayType: 'object',
  fields: simpleObjectSchemaFixture.splattedEditorFields.fields,
};

export const arrayObjectSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema: originalSchema,
};
