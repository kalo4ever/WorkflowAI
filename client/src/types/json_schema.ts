import { captureMessage } from '@sentry/nextjs';

export type JsonSchemaType = 'string' | 'number' | 'integer' | 'boolean' | 'object' | 'array' | 'null';

export interface BaseSchema {
  title?: string;
  description?: string;
  nullable?: boolean; // nullable is set to true if the schema is an anyOf with a null
  examples?: unknown[];
  default?: unknown;
  type?: JsonSchemaType;
  followedRefName?: string; // the last name of the ref that was followed to resolve this schema
  format?: string;
}

// We disable the no-use-before-define rule here because the type definition is recursive
/* eslint-disable no-use-before-define */
export type JsonValueSchema =
  | JsonObjectSchema
  | JsonArraySchema
  | JsonStringSchema
  | JsonNumberSchema
  | JsonBooleanSchema
  | JsonNullSchema
  | JsonAnyOfSchema
  | JsonOneOfSchema
  | JsonAllOfSchema
  | JsonRefSchema;
/* eslint-enable no-use-before-define */

export interface JsonObjectSchema extends BaseSchema {
  type?: 'object';
  properties?: { [key: string]: JsonValueSchema };
  additionalProperties?: boolean | JsonValueSchema;
  patternProperties?: { [pattern: string]: JsonValueSchema };
  required?: string[];
}

export interface JsonArraySchema extends BaseSchema {
  type: 'array';
  items?: false | JsonValueSchema | JsonValueSchema[];
  prefixItems?: JsonValueSchema[];
}

export type JsonSchemaDefinitions = { [key: string]: JsonValueSchema };

export type JsonSchema = (JsonObjectSchema | JsonArraySchema) & {
  $defs?: JsonSchemaDefinitions;
};

export type JsonStringFormat = 'date-time' | 'date' | 'timezone' | 'html' | 'url';

export type JsonSchemaStringExtraFields = {
  format?: JsonStringFormat | string;
  enum?: string[];
  pattern?: string;
};
export type JsonStringSchema = BaseSchema &
  JsonSchemaStringExtraFields & {
    type: 'string';
    minLength?: number;
    maxLength?: number;
  };

export type JsonSchemaNumberExtraFields = {
  minimum?: number;
  maximum?: number;
};
export type JsonNumberSchema = BaseSchema &
  JsonSchemaNumberExtraFields & {
    type: 'number' | 'integer';
  };

export interface JsonBooleanSchema extends BaseSchema {
  type: 'boolean';
}

export interface JsonNullSchema extends BaseSchema {
  type: 'null';
}

export interface JsonAnyOfSchema extends BaseSchema {
  anyOf: JsonValueSchema[];
  type?: undefined;
}

export interface JsonOneOfSchema extends BaseSchema {
  oneOf: JsonValueSchema[];
  type?: undefined;
}

export interface JsonAllOfSchema extends BaseSchema {
  allOf: JsonValueSchema[];
  type?: undefined;
}

export interface JsonRefSchema extends BaseSchema {
  $ref: string;
  type?: undefined;
}

class InvalidSchemaError extends Error {
  key: string;
  schema: JsonValueSchema;

  constructor(message: string, key: string, schema: JsonValueSchema) {
    super(message);
    this.name = 'InvalidSchemaError';
    this.key = key;
    this.schema = schema;
  }
}

function getSubSchemaNoRef(current: JsonValueSchema, key: string): JsonValueSchema {
  if (current.type === 'object' || 'properties' in current) {
    const next = current?.properties?.[key];
    if (next) {
      return next;
    }
    if (current.additionalProperties && typeof current.additionalProperties === 'object') {
      return current.additionalProperties;
    }
    throw new InvalidSchemaError(`Invalid schema key ${key}`, key, current);
  }

  if (current.type === 'array') {
    const next = current.items;
    const idx = parseInt(key, 10);
    if (Number.isNaN(idx)) {
      throw new InvalidSchemaError(`Invalid schema key for array index`, key, current);
    }

    if (Array.isArray(next)) {
      return next[idx];
    }
    if (next) return next;
    throw new InvalidSchemaError(`Invalid schema key for array`, key, current);
  }
  // TODO: we should likely never hit this line and raise an error instead of returning current
  captureMessage('getSubSchemaNoRef is returning the same schema', {
    extra: {
      current,
      key,
    },
  });
  return current;
}

function filterAnyOneAllOf(
  schema: JsonValueSchema,
  type: 'anyOf' | 'allOf' | 'oneOf',
  items: JsonValueSchema[],
  addNullable: boolean
): JsonValueSchema {
  const filtered = items.filter((s) => s.type !== 'null');
  if (filtered.length === 1) {
    const filteredSchemaWithMetadata = {
      ...schema,
      ...filtered[0],
    };
    return addNullable
      ? {
          nullable: filtered.length < items.length,
          ...filteredSchemaWithMetadata,
        }
      : filteredSchemaWithMetadata;
  }
  return { ...schema, [type]: filtered };
}

export function ignoreNulls(schema: JsonValueSchema, addNullable: boolean = false): JsonValueSchema {
  if ('anyOf' in schema && schema.anyOf) {
    const { anyOf, ...rest } = schema;
    return filterAnyOneAllOf(rest, 'anyOf', anyOf, addNullable);
  }
  if ('oneOf' in schema && schema.oneOf) {
    const { oneOf, ...rest } = schema;
    return filterAnyOneAllOf(rest, 'oneOf', oneOf, addNullable);
  }
  if ('allOf' in schema && schema.allOf) {
    const { allOf, ...rest } = schema;
    return filterAnyOneAllOf(rest, 'allOf', allOf, addNullable);
  }
  return schema;
}

export function sanitizeRef(ref: string) {
  if (!ref.startsWith('#/$defs/')) {
    throw new InvalidSchemaError(`Invalid ref`, ref, { $ref: ref });
  }
  const key = ref.substring('#/$defs/'.length);
  if (key.includes('/')) {
    throw new InvalidSchemaError(`Invalid nested ref`, ref, { $ref: ref });
  }
  return key;
}

export function extractSchemaRefName(schema: JsonValueSchema | undefined, key: string) {
  if (!schema) {
    return undefined;
  }
  let next = undefined;
  if (schema.type === 'object') {
    next = schema.properties?.[key];
  }
  if (schema.type === 'array') {
    next = schema.items;
  }
  if (!next) {
    return undefined;
  }
  if ('$ref' in next) {
    return sanitizeRef(next.$ref);
  } else if ('anyOf' in next) {
    const ref = next.anyOf.find((s) => '$ref' in s) as JsonRefSchema | undefined;
    if (ref) {
      return sanitizeRef(ref.$ref);
    }
  } else if ('oneOf' in next) {
    const ref = next.oneOf.find((s) => '$ref' in s) as JsonRefSchema | undefined;
    if (ref) {
      return sanitizeRef(ref.$ref);
    }
  } else if ('allOf' in next) {
    const ref = next.allOf.find((s) => '$ref' in s) as JsonRefSchema | undefined;
    if (ref) {
      return sanitizeRef(ref.$ref);
    }
  }
  return undefined;
}

/**
 * Makes sure the current schema does not contain anyOf, oneOf, allOf or $ref
 */
export function sanitizeSchema(schema: JsonValueSchema, defs: JsonSchemaDefinitions | undefined) {
  const next = ignoreNulls(schema, true);
  if ('$ref' in next && next.$ref) {
    const refName = sanitizeRef(next.$ref);
    const def = defs?.[refName];
    if (def) {
      return {
        // Some refs like audio can have a format
        format: schema.format,
        ...def,
        nullable: next.nullable,
        followedRefName: refName,
      };
    }
    throw new InvalidSchemaError(`Missing ref`, '', schema);
  }
  return next;
}
/**
 * Retrieves a sub schema of the current schema
 * - If the sub schema is a ref, it will be resolved
 * - If the sub schema is an anyOf, nulls are ignored
 */
export function getSubSchema(
  current: JsonValueSchema,
  defs: JsonSchemaDefinitions | undefined,
  key: string
): JsonValueSchema {
  return sanitizeSchema(getSubSchemaNoRef(current, key), defs);
}

export function getSubSchemaOptional(
  current: JsonValueSchema,
  defs: JsonSchemaDefinitions | undefined,
  key: string
): JsonValueSchema | undefined {
  try {
    return getSubSchema(current, defs, key);
  } catch (e) {
    if (e instanceof InvalidSchemaError) {
      return undefined;
    }
    throw e;
  }
}

export function joinKeyPath(keyPath: string, key: string) {
  return keyPath ? `${keyPath}.${key}` : key;
}
