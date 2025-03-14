import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonValueSchema } from '@/types';

export type SchemaEditorTextCaseFixture = {
  originalSchema: JsonValueSchema;
  splattedEditorFields: SchemaEditorField;
  finalSchema: JsonValueSchema;
};
