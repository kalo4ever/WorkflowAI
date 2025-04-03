import {
  JsonSchema,
  JsonSchemaDefinitions,
  JsonValueSchema,
  getSubSchema,
  getSubSchemaOptional,
  sanitizeRef,
} from '@/types';
import { FILE_REF_NAMES } from './constants';

export function isFileSchema(schema: JsonValueSchema | undefined): boolean {
  if (schema?.type === 'object' && !!schema.followedRefName && FILE_REF_NAMES.includes(schema.followedRefName)) {
    return true;
  }

  if (!!schema && '$ref' in schema) {
    const refName = sanitizeRef(schema.$ref);
    if (FILE_REF_NAMES.includes(refName)) {
      return true;
    }
  }
  return false;
}

function innerReplaceFileDataWithURL(
  schema: JsonValueSchema | undefined,
  defs: JsonSchemaDefinitions | undefined,
  obj: unknown,
  replacer: (obj: Record<string, unknown>, schema: JsonValueSchema) => Record<string, unknown>
): unknown {
  if (!obj || typeof obj !== 'object' || !schema) {
    return obj;
  }
  // We retrieve all sub schemas optionally since sometimes we have freefrom objects
  if (!isFileSchema(schema)) {
    if (Array.isArray(obj)) {
      return obj.map((item, idx) =>
        innerReplaceFileDataWithURL(getSubSchemaOptional(schema, defs, idx.toString()), defs, item, replacer)
      );
    }
    // We dive into the object to replace the file data with the URL
    return Object.entries(obj).reduce(
      (acc, [key, value]) => {
        acc[key] = innerReplaceFileDataWithURL(getSubSchemaOptional(schema, defs, key), defs, value, replacer);
        return acc;
      },
      {} as Record<string, unknown>
    );
  }
  return replacer(obj as Record<string, unknown>, schema);
}

export function replaceFileData(
  schema: JsonSchema,
  obj: Record<string, unknown>,
  replacer: (obj: Record<string, unknown>, schema: JsonValueSchema) => Record<string, unknown>
): Record<string, unknown> {
  return innerReplaceFileDataWithURL(schema, schema.$defs, obj, replacer) as Record<string, unknown>;
}

export function requiresFileSupport(
  schema: JsonValueSchema | undefined,
  defs: JsonSchemaDefinitions | undefined
): boolean {
  if (schema === undefined || defs === undefined) {
    return false;
  }

  if (
    schema.followedRefName === 'Image' ||
    schema.followedRefName === 'Audio' ||
    schema.followedRefName === 'Video' ||
    schema.followedRefName === 'Document' ||
    schema.followedRefName === 'File'
  ) {
    return true;
  }

  if ('properties' in schema && schema.properties) {
    for (const key in schema.properties) {
      const subSchema = getSubSchema(schema, defs, key);
      if (requiresFileSupport(subSchema, defs)) {
        return true;
      }
    }
  }

  if ('items' in schema && schema.items) {
    if (Array.isArray(schema.items)) {
      for (const idx in schema.items) {
        if (requiresFileSupport(getSubSchema(schema, defs, idx), defs)) {
          return true;
        }
      }
    } else {
      if (requiresFileSupport(getSubSchema(schema, defs, '0'), defs)) {
        return true;
      }
    }
  }

  return false;
}
