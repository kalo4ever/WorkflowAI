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

export type FileFormat = 'audio' | 'image' | 'text' | 'document';

function appendToFormats(
  schema: JsonValueSchema | undefined,
  defs: JsonSchemaDefinitions | undefined,
  formats: Set<FileFormat>
) {
  if (schema === undefined || defs === undefined) {
    return;
  }

  if (schema.followedRefName === 'Image') {
    formats.add('image');
  }

  if (schema.followedRefName === 'File') {
    switch (schema.format) {
      case 'audio':
        formats.add('audio');
        break;
      case 'image':
        formats.add('image');
        break;
      case 'pdf':
      case 'text':
      case 'document':
        formats.add('document');
        break;
      default:
        // TODO: how should we handle a file without a format?
        break;
    }
  }

  if ('properties' in schema && schema.properties) {
    for (const key in schema.properties) {
      const subSchema = getSubSchema(schema, defs, key);
      appendToFormats(subSchema, defs, formats);
    }
  }

  if ('items' in schema && schema.items) {
    if (Array.isArray(schema.items)) {
      for (const idx in schema.items) {
        appendToFormats(getSubSchema(schema, defs, idx), defs, formats);
      }
    } else {
      appendToFormats(getSubSchema(schema, defs, '0'), defs, formats);
    }
  }
}

export function extractFormats(schema: JsonSchema | undefined | null): FileFormat[] | undefined {
  if (schema === undefined || schema === null) {
    return undefined;
  }
  const formats = new Set<FileFormat>();
  appendToFormats(schema, schema.$defs, formats);
  if (formats.size === 0) {
    return undefined;
  }
  return Array.from(formats);
}
