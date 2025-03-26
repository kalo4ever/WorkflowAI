import { JsonSchema } from '@/types/json_schema';

export function collectUsedDefinitions(schema: JsonSchema): Record<string, JsonSchema> {
  const usedDefs: Record<string, JsonSchema> = {};

  function traverse(node: JsonSchema) {
    if (!node || typeof node !== 'object') return;

    if ('$ref' in node && typeof node.$ref === 'string') {
      const defName = node.$ref.replace('#/$defs/', '');
      if (!usedDefs[defName]) {
        usedDefs[defName] = { type: 'object' };
      }
    }

    Object.values(node).forEach((value) => {
      if (typeof value === 'object' && value !== null) {
        traverse(value as Record<string, unknown>);
      }
    });
  }

  traverse(schema);
  return usedDefs;
}
