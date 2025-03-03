import cloneDeep from 'lodash/cloneDeep';
import { JsonSchema } from '@/types';
import { hydrateRefs } from './json-schema/json-schema-refs';
import { compile } from './json-schema/json-schema-to-typescript';
import { sanitize } from './json-schema/sanitize-json-schema';

const excludedRefsForCodegen = new Set(['File', 'Image', 'DatetimeLocal']);

export async function schemaToTS(title: string, jsonSchema: JsonSchema) {
  const schemaClone = cloneDeep(jsonSchema);
  if ('title' in schemaClone) {
    schemaClone.title = undefined;
  }
  const existingWAIRefs = new Set<string>();
  // We replace the excluded refs with empty objects to allow removing the generated types
  if ('$defs' in schemaClone && typeof schemaClone.$defs === 'object') {
    for (const key of Object.keys(schemaClone.$defs)) {
      if (excludedRefsForCodegen.has(key)) {
        schemaClone.$defs[key] = {};
        existingWAIRefs.add(key);
      }
    }
  }

  // @ts-expect-error JsonSchema conflicts with Record<string, unknown>
  const resolvedJsonSchema = hydrateRefs(sanitize(schemaClone), {
    keepRefs: false,
  });
  let compiled = await compile(resolvedJsonSchema, title, {
    unreachableDefinitions: false,
    ignoreMinAndMaxItems: true,
    format: false,
    additionalProperties: false,
    bannerComment: '',
  });
  for (const ref of existingWAIRefs) {
    compiled = compiled.replace(`export type ${ref} = unknown\n\n`, '');
  }

  return { compiled, existingWAIRefs };
}
