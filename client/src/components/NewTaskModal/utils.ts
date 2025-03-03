import { SchemaEditorField } from '@/lib/schemaEditorUtils';

export function getNumberOfLinesInSchema(schema: SchemaEditorField): number {
  let result = 1;
  schema.fields?.forEach((field) => {
    result += getNumberOfLinesInSchema(field);
  });
  return result;
}
