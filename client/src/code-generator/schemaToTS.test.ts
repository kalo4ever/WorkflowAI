import { JsonSchema } from '@/types';
import { schemaToTS } from './schemaToTS';

const DEFS = {
  DatetimeLocal: {
    additionalProperties: false,
    description: 'This class represents a local datetime, with a datetime and a timezone.',
    properties: {
      date: {
        description: 'The date of the local datetime.',
        format: 'date',
        type: 'string',
      },
      local_time: {
        description: 'The time of the local datetime without timezone info.',
        format: 'time',
        type: 'string',
      },
      timezone: {
        description: 'The timezone of the local time.',
        type: 'string',
      },
    },
    required: ['date', 'local_time', 'timezone'],
    type: 'object',
  },
  Image: {
    additionalProperties: false,
    properties: {
      content_type: {
        description: 'The content type of the image',
        enum: ['image/png', 'image/jpg', 'image/jpeg', 'image/webp', 'image/tiff', 'image/gif'],
        type: 'string',
      },
      data: {
        anyOf: [
          {
            anyOf: [
              {
                contentEncoding: 'base64',
                type: 'string',
              },
              {
                pattern: '^data:[^;]*;base64,[-A-Za-z0-9+/]+={0,3}$',
                type: 'string',
              },
              {
                anyOf: [{}, {}],
              },
            ],
          },
          {
            $ref: '#/$defs/Image/properties/data/anyOf/0',
          },
        ],
        description: 'The Buffer or base64 encoded data of the image',
      },
      name: {
        description: 'An optional name',
        type: 'string',
      },
    },
    required: ['content_type', 'data'],
    type: 'object',
  },
};

describe('schemaToTS', () => {
  it('should convert JSON schema with definitions to TS', async () => {
    const mockJsonSchema: JsonSchema = {
      type: 'object',
      properties: {
        p: { $ref: '#/$defs/person' },
      },
      $defs: {
        person: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            address: { $ref: '#/$defs/address' },
          },
          required: ['name', 'address'],
        },
        address: {
          type: 'object',
          properties: {
            street: { type: 'string' },
            city: { type: 'string' },
            state: { type: 'string' },
          },
          required: ['street', 'city', 'state'],
        },
      },
    };

    const { compiled: ts, existingWAIRefs } = await schemaToTS('PersonTaskInput', mockJsonSchema);
    expect(existingWAIRefs).toEqual(new Set());
    expect(ts).toBe(`export interface PersonTaskInput {
p?: Person
}
export interface Person {
name: string
address: Address
}
export interface Address {
street: string
city: string
state: string
}
`);
  });

  it('should convert JSON schema with datetimeLocal definition to TS', async () => {
    const mockJsonSchema = {
      type: 'object',
      properties: {
        e: { $ref: '#/$defs/event' },
      },
      $defs: {
        DatetimeLocal: DEFS.DatetimeLocal,
        event: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            date: { $ref: '#/$defs/DatetimeLocal' },
          },
          required: ['name', 'date'],
        },
      },
    };
    const { compiled: ts, existingWAIRefs } = await schemaToTS('EventTaskInput', mockJsonSchema as JsonSchema);
    expect(existingWAIRefs).toEqual(new Set(['DatetimeLocal']));
    expect(ts).toBe(`export interface EventTaskInput {
e?: Event
}
export interface Event {
name: string
date: DatetimeLocal
}
`);
  });

  it('should convert JSON schema with Image definition to TS', async () => {
    const mockJsonSchema = {
      type: 'object',
      properties: {
        i: { $ref: '#/$defs/Image' },
      },
      $defs: {
        Image: DEFS.Image,
      },
    };
    const { compiled: ts, existingWAIRefs } = await schemaToTS('EventTaskInput', mockJsonSchema as JsonSchema);
    expect(existingWAIRefs).toEqual(new Set(['Image']));
    expect(ts).toBe(`export interface EventTaskInput {
i?: Image
}
`);
  });
});
