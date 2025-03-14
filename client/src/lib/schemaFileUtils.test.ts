import { JsonSchema } from '@/types';
import { extractFormats } from './schemaFileUtils';

describe('extractFormats', () => {
  it('is undefined when the TaskSchema is undefined', () => {
    expect(extractFormats(undefined)).toEqual(undefined);
  });

  it('is undefined when the TaskSchema is null', () => {
    expect(extractFormats(null)).toEqual(undefined);
  });

  it('is undefined when the input_schema does not have an Image key', () => {
    const subject: JsonSchema = {
      $defs: {},
    };
    expect(extractFormats(subject)).toEqual(undefined);
  });

  it('is "images" when the input_schema has empty defs', () => {
    const subject: JsonSchema = {
      $defs: {
        Image: {},
      },
      properties: {
        image: {
          $ref: '#/$defs/Image',
        },
      },
    };
    expect(extractFormats(subject)).toEqual(['image']);
  });

  it('is "audio" when the input_schema has an audio format', () => {
    const subject: JsonSchema = {
      $defs: {
        File: {},
      },
      properties: {
        file: {
          $ref: '#/$defs/File',
          format: 'audio',
        },
      },
    };
    expect(extractFormats(subject)).toEqual(['audio']);
  });
});
