import { JsonSchema, JsonValueSchema } from '@/types';
import { requiresFileSupport } from './schemaFileUtils';

describe('requiresFileSupport', () => {
  it('returns false when schema is undefined', () => {
    expect(requiresFileSupport(undefined, {})).toBe(false);
  });

  it('returns false when defs is undefined', () => {
    const schema: JsonValueSchema = {
      type: 'object',
      properties: {},
    };
    expect(requiresFileSupport(schema, undefined)).toBe(false);
  });

  it('returns false when schema has no file-related references', () => {
    const schema: JsonSchema = {
      $defs: {},
      properties: {
        text: { type: 'string' },
      },
    };
    expect(requiresFileSupport(schema, schema.$defs)).toBe(false);
  });

  it('returns true when schema has an Image reference', () => {
    const schema: JsonSchema = {
      $defs: {
        Image: {},
      },
      properties: {
        image: {
          $ref: '#/$defs/Image',
        },
      },
    };
    expect(requiresFileSupport(schema, schema.$defs)).toBe(true);
  });

  it('returns true when schema has an Audio reference', () => {
    const schema: JsonSchema = {
      $defs: {
        Audio: {},
      },
      properties: {
        audio: {
          $ref: '#/$defs/Audio',
        },
      },
    };
    expect(requiresFileSupport(schema, schema.$defs)).toBe(true);
  });

  it('returns true when schema has nested file references', () => {
    const schema: JsonSchema = {
      $defs: {
        Image: {},
      },
      properties: {
        nested: {
          type: 'object',
          properties: {
            image: {
              $ref: '#/$defs/Image',
            },
          },
        },
      },
    };
    expect(requiresFileSupport(schema, schema.$defs)).toBe(true);
  });

  it('returns true when schema has file references in array items', () => {
    const schema: JsonSchema = {
      $defs: {
        Image: {},
      },
      properties: {
        images: {
          type: 'array',
          items: {
            $ref: '#/$defs/Image',
          },
        },
      },
    };
    expect(requiresFileSupport(schema, schema.$defs)).toBe(true);
  });
});
