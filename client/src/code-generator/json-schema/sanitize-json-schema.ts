import { JsonSchema } from '@/types';

export function sanitize(obj: JsonSchema) {
  if (!('type' in obj)) {
    if (
      'properties' in obj ||
      'patternProperties' in obj ||
      'propertyNames' in obj ||
      'minProperties' in obj ||
      'maxProperties' in obj
    ) {
      obj.type = 'object';
    } else if (
      'items' in obj ||
      'prefixItems' in obj ||
      'contains' in obj ||
      'uniqueItems' in obj ||
      'minItems' in obj ||
      'maxItems' in obj
    ) {
      // @ts-expect-error not sure why TS is complaining here
      obj.type = 'array';
    }
  }

  // Remove description so that it does not show in the codegen
  if ('description' in obj) {
    delete obj.description;
  }

  if ('properties' in obj) {
    //@ts-expect-error we can ignore the typing of properties here
    for (const [key, value] of Object.entries(obj.properties)) {
      if (typeof value === 'object' && value !== null) {
        // @ts-expect-error value does not have the correct index signature
        obj.properties[key] = sanitize(value);
      }
    }
  }

  if ('items' in obj) {
    if (typeof obj.items === 'object' && obj.items !== null) {
      if (Array.isArray(obj.items)) {
        // @ts-expect-error we can ignore the typing of items here
        obj.items = obj.items.map((item) => sanitize(item));
      } else {
        // @ts-expect-error we can ignore the typing of items here
        obj.items = sanitize(obj.items);
      }
    }
  }

  return obj;
}
