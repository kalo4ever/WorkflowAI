/* eslint-disable max-lines */
import { JsonSchema, JsonValueSchema } from '@/types';
import {
  InitInputFromSchemaMode,
  initInputFromSchema,
  mergeItems,
  mergeProperties,
  mergeRequiredFields,
  mergeSchemas,
  parseSchemaNode,
} from './schemaUtils';

describe('parseSchemaNode', () => {
  const TABLE = [
    { type: 'string', expectedVoid: '', expectedNonVoid: 'string' },
    { type: 'number', expectedVoid: 0, expectedNonVoid: 'number' },
    { type: 'integer', expectedVoid: 0, expectedNonVoid: 'integer' },
    { type: 'boolean', expectedVoid: false, expectedNonVoid: 'boolean' },
    { type: 'object', expectedVoid: null, expectedNonVoid: 'object' },
    { type: 'array', expectedVoid: null, expectedNonVoid: 'array' },
    { type: 'null', expectedVoid: null, expectedNonVoid: 'undefined' },
  ] as const;

  describe.each(TABLE)(
    'type is $type',
    ({ type, expectedVoid, expectedNonVoid }) => {
      const schema = { type };
      it(`is "${expectedVoid}" when void result is enabled`, () => {
        const result = parseSchemaNode(
          schema,
          {},
          InitInputFromSchemaMode.VOID
        );
        expect(result).toEqual(expectedVoid);
      });
      it(`is "${expectedNonVoid}" when void result is disabled`, () => {
        const result = parseSchemaNode(
          schema,
          {},
          InitInputFromSchemaMode.TYPE
        );
        expect(result).toEqual(expectedNonVoid);
      });
    }
  );

  describe('type is object', () => {
    const SAMPLE_JSON_SCHEMA: JsonValueSchema = {
      type: 'object',
      properties: {
        name: {
          type: 'string',
        },
        age: {
          type: 'integer',
        },
        address: {
          type: 'object',
          properties: {
            street: {
              type: 'string',
            },
            city: {
              type: 'string',
            },
            zipcode: {
              type: 'string',
            },
          },
          required: ['street', 'city'],
        },
        isActive: {
          type: 'boolean',
        },
      },
      required: ['name', 'age', 'address'],
    };

    test('"add void" result is disabled', () => {
      const result = parseSchemaNode(
        SAMPLE_JSON_SCHEMA,
        {},
        InitInputFromSchemaMode.TYPE
      );
      expect(result).toEqual({
        name: 'string',
        age: 'integer',
        address: {
          street: 'string',
          city: 'string',
          zipcode: 'string',
        },
        isActive: 'boolean',
      });
    });
    test('"add void" result is enabled', () => {
      const result = parseSchemaNode(
        SAMPLE_JSON_SCHEMA,
        {},
        InitInputFromSchemaMode.VOID
      );
      expect(result).toEqual({
        name: '',
        age: 0,
        address: {
          street: '',
          city: '',
          zipcode: '',
        },
        isActive: false,
      });
    });
  });
});

describe('initInputFromSchema', () => {
  const schema: JsonSchema = {
    type: 'object',
    properties: {
      currentYear: {
        type: 'number',
        description: 'Second input number',
        examples: [2, 10, -3],
      },
    },
    required: ['currentYear'],
  };
  it('initializes a number', () => {
    const result = initInputFromSchema(
      schema,
      {},
      InitInputFromSchemaMode.TYPE
    );
    expect(result).toEqual({ currentYear: 'number' });
  });
  it('initializes a number', () => {
    const result = initInputFromSchema(
      schema,
      {},
      InitInputFromSchemaMode.VOID
    );
    expect(result).toEqual({ currentYear: 0 });
  });
});

describe('mergeRequiredFields', () => {
  it('should merge required fields from both schemas', () => {
    const oldSchema: JsonValueSchema = {
      type: 'object' as const,
      required: ['name', 'age'],
    };
    const newSchema: JsonValueSchema = {
      type: 'object' as const,
      required: ['age', 'email'],
    };

    const result = mergeRequiredFields(oldSchema, newSchema);
    expect(result).toEqual(['name', 'age', 'email']);
  });

  it('should return undefined if both schemas have no required fields', () => {
    const oldSchema: JsonValueSchema = {
      type: 'object' as const,
    };
    const newSchema: JsonValueSchema = {
      type: 'object' as const,
    };

    const result = mergeRequiredFields(oldSchema, newSchema);
    expect(result).toBeUndefined();
  });

  it('should use new schema required fields if old schema has none', () => {
    const oldSchema: JsonValueSchema = {
      type: 'object' as const,
    };
    const newSchema: JsonValueSchema = {
      type: 'object' as const,
      required: ['name', 'email'],
    };

    const result = mergeRequiredFields(oldSchema, newSchema);
    expect(result).toEqual(['name', 'email']);
  });

  it('should use old schema required fields if new schema has none', () => {
    const oldSchema: JsonValueSchema = {
      type: 'object' as const,
      required: ['name', 'age'],
    };
    const newSchema: JsonValueSchema = {
      type: 'object' as const,
    };

    const result = mergeRequiredFields(oldSchema, newSchema);
    expect(result).toEqual(['name', 'age']);
  });

  it('should remove duplicates when merging required fields', () => {
    const oldSchema: JsonValueSchema = {
      type: 'object' as const,
      required: ['name', 'name', 'age'],
    };
    const newSchema: JsonValueSchema = {
      type: 'object' as const,
      required: ['age', 'age', 'email'],
    };

    const result = mergeRequiredFields(oldSchema, newSchema);
    expect(result).toEqual(['name', 'age', 'email']);
  });
});

describe('mergeSchemas - items merging', () => {
  it('should merge array items when both schemas have single item definitions', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string' },
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string' },
    };

    const result = mergeSchemas(oldSchema, newSchema);
    expect(result).toEqual({
      type: 'array',
      items: { type: 'string' },
    });
  });

  it('should merge array items when both schemas have tuple definitions', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: [{ type: 'string' }, { type: 'number', minimum: 0 }],
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: [
        { type: 'string', minLength: 5 },
        { type: 'number', maximum: 100 },
        { type: 'boolean' },
      ],
    };

    const result = mergeSchemas(oldSchema, newSchema);
    expect(result).toEqual({
      type: 'array',
      items: [
        { type: 'string', minLength: 5 },
        { type: 'number', minimum: 0, maximum: 100 },
        { type: 'boolean' },
      ],
    });
  });

  it('should use new schema items when old schema has no items', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string' },
    };

    const result = mergeSchemas(oldSchema, newSchema);
    expect(result).toEqual({
      type: 'array',
      items: { type: 'string' },
    });
  });

  it('should keep old schema items when new schema has no items', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string' },
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
    };

    const result = mergeSchemas(oldSchema, newSchema);
    expect(result).toEqual({
      type: 'array',
      items: { type: 'string' },
    });
  });

  it('should handle mixed item definitions (single vs tuple)', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string' },
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: [{ type: 'string', minLength: 5 }, { type: 'number' }],
    };

    const result = mergeSchemas(oldSchema, newSchema);
    expect(result).toEqual({
      type: 'array',
      items: [{ type: 'string', minLength: 5 }, { type: 'number' }],
    });
  });

  it('should handle nested array items', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: {
        type: 'array',
        items: { type: 'string', minLength: 1 },
      },
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: {
        type: 'array',
        items: { type: 'string', maxLength: 10 },
      },
    };

    const result = mergeSchemas(oldSchema, newSchema);
    expect(result).toEqual({
      type: 'array',
      items: {
        type: 'array',
        items: {
          type: 'string',
          minLength: 1,
          maxLength: 10,
        },
      },
    });
  });
});

describe('mergeItems', () => {
  it('should return undefined when both schemas have no items', () => {
    const oldSchema: JsonValueSchema = { type: 'array' };
    const newSchema: JsonValueSchema = { type: 'array' };

    const result = mergeItems(oldSchema, newSchema);
    expect(result).toBeUndefined();
  });

  it('should return new items when old schema has no items', () => {
    const oldSchema: JsonValueSchema = { type: 'array' };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string' },
    };

    const result = mergeItems(oldSchema, newSchema);
    expect(result).toEqual({ type: 'string' });
  });

  it('should return old items when new schema has no items', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'number' },
    };
    const newSchema: JsonValueSchema = { type: 'array' };

    const result = mergeItems(oldSchema, newSchema);
    expect(result).toEqual({ type: 'number' });
  });

  it('should merge single item definitions', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string', format: 'date' },
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string', description: 'A date string' },
    };

    const result = mergeItems(oldSchema, newSchema);
    expect(result).toEqual({
      type: 'string',
      format: 'date',
      description: 'A date string',
    });
  });

  it('should merge tuple definitions', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: [{ type: 'string' }, { type: 'number', description: 'A number' }],
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: [
        { type: 'string', format: 'email' },
        { type: 'number' },
        { type: 'boolean' },
      ],
    };

    const result = mergeItems(oldSchema, newSchema);
    expect(result).toEqual([
      { type: 'string', format: 'email' },
      { type: 'number', description: 'A number' },
      { type: 'boolean' },
    ]);
  });

  it('should prefer new schema when mixing single and tuple definitions', () => {
    const oldSchema: JsonValueSchema = {
      type: 'array',
      items: { type: 'string', format: 'date' },
    };
    const newSchema: JsonValueSchema = {
      type: 'array',
      items: [{ type: 'string' }, { type: 'number' }],
    };

    const result = mergeItems(oldSchema, newSchema);
    expect(result).toEqual([{ type: 'string' }, { type: 'number' }]);
  });
});

describe('mergeProperties', () => {
  it('should return undefined when both schemas have no properties', () => {
    const oldSchema: JsonValueSchema = { type: 'object' };
    const newSchema: JsonValueSchema = { type: 'object' };

    const result = mergeProperties(oldSchema, newSchema);
    expect(result).toBeUndefined();
  });

  it('should return new properties when old schema has none', () => {
    const oldSchema: JsonValueSchema = { type: 'object' };
    const newSchema: JsonValueSchema = {
      type: 'object',
      properties: {
        name: { type: 'string' },
      },
    };

    const result = mergeProperties(oldSchema, newSchema);
    expect(result).toEqual({
      name: { type: 'string' },
    });
  });

  it('should return old properties when new schema has none', () => {
    const oldSchema: JsonValueSchema = {
      type: 'object',
      properties: {
        age: { type: 'number' },
      },
    };
    const newSchema: JsonValueSchema = { type: 'object' };

    const result = mergeProperties(oldSchema, newSchema);
    expect(result).toEqual({
      age: { type: 'number' },
    });
  });

  it('should merge properties from both schemas', () => {
    const oldSchema: JsonValueSchema = {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'The name' },
        age: { type: 'number' },
      },
    };
    const newSchema: JsonValueSchema = {
      type: 'object',
      properties: {
        name: { type: 'string', format: 'text' },
        email: { type: 'string', format: 'email' },
      },
    };

    const result = mergeProperties(oldSchema, newSchema);
    expect(result).toEqual({
      name: { type: 'string', description: 'The name', format: 'text' },
      age: { type: 'number' },
      email: { type: 'string', format: 'email' },
    });
  });

  it('should handle nested object properties', () => {
    const oldSchema: JsonValueSchema = {
      type: 'object',
      properties: {
        address: {
          type: 'object',
          properties: {
            street: { type: 'string' },
            city: { type: 'string', description: 'The city' },
          },
        },
      },
    };
    const newSchema: JsonValueSchema = {
      type: 'object',
      properties: {
        address: {
          type: 'object',
          properties: {
            city: { type: 'string', format: 'text' },
            country: { type: 'string' },
          },
        },
      },
    };

    const result = mergeProperties(oldSchema, newSchema);
    expect(result).toEqual({
      address: {
        type: 'object',
        properties: {
          street: { type: 'string' },
          city: { type: 'string', description: 'The city', format: 'text' },
          country: { type: 'string' },
        },
      },
    });
  });
});
