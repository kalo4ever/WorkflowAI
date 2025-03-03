/* eslint-disable max-lines */
import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonObjectSchema, JsonSchemaDefinitions } from '@/types';
import { TEST_IMAGE_SCHEMA } from './imageSchema';
import { SchemaEditorTextCaseFixture } from './types';

const unionObjectsOriginalDefinitions: JsonSchemaDefinitions = {
  DatetimeLocal: {
    description:
      'This class represents a local datetime, with a datetime and a timezone.',
    properties: {
      date: {
        description: 'The date of the local datetime.',
        examples: ['2023-03-01'],
        format: 'date',
        title: 'Date',
        type: 'string',
      },
      local_time: {
        description: 'The time of the local datetime without timezone info.',
        examples: ['12:00:00', '22:00:00'],
        format: 'time',
        title: 'Local Time',
        type: 'string',
      },
      timezone: {
        description: 'The timezone of the local time.',
        examples: ['Europe/Paris', 'America/New_York'],
        format: 'timezone',
        title: 'Timezone',
        type: 'string',
      },
    },
    required: ['date', 'local_time', 'timezone'],
    title: 'DatetimeLocal',
    type: 'object',
  },
  EnumExample: {
    enum: ['Option1', 'Option2', 'Option3'],
    title: 'EnumExample',
    type: 'string',
  },
  Image: TEST_IMAGE_SCHEMA,
  NestedObjectExampleWithImage: {
    properties: {
      nested_string_example: {
        description: 'A simple string field',
        examples: ['Sample text'],
        title: 'Nested String Example',
        type: 'string',
      },
      nested_fuzzy_string_example: {
        description: 'A fuzzy string field',
        examples: ['Sample fuzzy string'],
        title: 'Nested Fuzzy String Example',
        type: 'string',
      },
      nested_integer_example: {
        description: 'A simple integer field',
        examples: [42],
        title: 'Nested Integer Example',
        type: 'integer',
      },
      nested_float_example: {
        description: 'A simple float field',
        examples: [3.14],
        title: 'Nested Float Example',
        type: 'number',
      },
      nested_boolean_example: {
        description: 'A simple boolean field',
        examples: [true],
        title: 'Nested Boolean Example',
        type: 'boolean',
      },
      nested_datetime_example: {
        description: 'A date-time string in ISO 8601 format',
        examples: ['2023-04-05T14:30:00Z'],
        format: 'date-time',
        title: 'Nested Datetime Example',
        type: 'string',
      },
      nested_datetime_local_example: {
        allOf: [
          {
            $ref: '#/$defs/DatetimeLocal',
          },
        ],
        description: 'A DateTimeLocal field',
      },
      nested_email_example: {
        description: 'A string formatted as an email address',
        examples: ['user@example.com'],
        format: 'email',
        title: 'Nested Email Example',
        type: 'string',
      },
      nested_html_string_example: {
        description: 'An HTMLString field',
        examples: ['<p>HTML text</p>'],
        format: 'html',
        title: 'Nested Html String Example',
        type: 'string',
      },
      nested_enum_example: {
        allOf: [
          {
            $ref: '#/$defs/EnumExample',
          },
        ],
        description: 'An enumeration with predefined options',
      },
      nested_https_url_example: {
        description: 'A string formatted as an HTTPS URL',
        examples: ['https://example.com'],
        format: 'url',
        title: 'Nested Https Url Example',
        type: 'string',
      },
      nested_time_zone_example: {
        description: 'A string formatted as a time zone',
        examples: ['America/New_York'],
        format: 'timezone',
        title: 'Nested Time Zone Example',
        type: 'string',
      },
      nested_dict_example: {
        additionalProperties: {
          type: 'string',
        },
        description: 'A simple dictionary field',
        examples: [
          {
            key: 'value',
          },
        ],
        title: 'Nested Dict Example',
        type: 'object',
        properties: {},
      },
      nested_image: {
        allOf: [
          {
            $ref: '#/$defs/Image',
          },
        ],
        description: 'An image field',
      },
    },
    required: [
      'nested_string_example',
      'nested_fuzzy_string_example',
      'nested_integer_example',
      'nested_float_example',
      'nested_boolean_example',
      'nested_datetime_example',
      'nested_datetime_local_example',
      'nested_email_example',
      'nested_html_string_example',
      'nested_enum_example',
      'nested_https_url_example',
      'nested_time_zone_example',
      'nested_dict_example',
      'nested_image',
    ],
    title: 'NestedObjectExampleWithImage',
    type: 'object',
  },
};

const originalSchema: JsonObjectSchema = {
  properties: {
    string_example: {
      description: 'A simple string field',
      examples: ['Sample text'],
      title: 'String Example',
      type: 'string',
    },
    fuzzy_string_example: {
      description: 'A fuzzy string field',
      examples: ['Sample fuzzy string'],
      title: 'Fuzzy String Example',
      type: 'string',
    },
    integer_example: {
      description: 'A simple integer field',
      examples: [42],
      title: 'Integer Example',
      type: 'integer',
    },
    float_example: {
      description: 'A simple float field',
      examples: [3.14],
      title: 'Float Example',
      type: 'number',
    },
    boolean_example: {
      description: 'A simple boolean field',
      examples: [true],
      title: 'Boolean Example',
      type: 'boolean',
    },
    datetime_example: {
      description: 'A date-time string in ISO 8601 format',
      examples: ['2023-04-05T14:30:00Z'],
      format: 'date-time',
      title: 'Datetime Example',
      type: 'string',
    },
    datetime_local_example: {
      allOf: [
        {
          $ref: '#/$defs/DatetimeLocal',
        },
      ],
      description: 'A DateTimeLocal field',
    },
    email_example: {
      description: 'A string formatted as an email address',
      examples: ['user@example.com'],
      format: 'email',
      title: 'Email Example',
      type: 'string',
    },
    html_string_example: {
      description: 'An HTMLString field',
      examples: ['<p>HTML text</p>'],
      format: 'html',
      title: 'Html String Example',
      type: 'string',
    },
    enum_example: {
      allOf: [
        {
          $ref: '#/$defs/EnumExample',
        },
      ],
      description: 'An enumeration with predefined options',
    },
    https_url_example: {
      description: 'A string formatted as an HTTPS URL',
      examples: ['https://example.com'],
      format: 'url',
      title: 'Https Url Example',
      type: 'string',
    },
    time_zone_example: {
      description: 'A string formatted as a time zone',
      examples: ['America/New_York'],
      format: 'timezone',
      title: 'Time Zone Example',
      type: 'string',
    },
    dict_example: {
      additionalProperties: {
        type: 'string',
      },
      description: 'A simple dictionary field',
      examples: [
        {
          key: 'value',
        },
      ],
      properties: {},
      title: 'Dict Example',
      type: 'object',
    },
    nested_object_example: {
      allOf: [
        {
          $ref: '#/$defs/NestedObjectExampleWithImage',
        },
      ],
      description: 'A nested object example',
    },
    image_example: {
      allOf: [
        {
          $ref: '#/$defs/Image',
        },
      ],
      description: 'An image field',
    },
    string_example_list: {
      description: 'A list of simple string fields',
      examples: [['Sample text 1', 'Sample text 2']],
      items: {
        type: 'string',
      },
      title: 'String Example List',
      type: 'array',
    },
    fuzzy_string_example_list: {
      description: 'A list of fuzzy string fields',
      examples: [['Sample fuzzy string 1', 'Sample fuzzy string 2']],
      items: {
        type: 'string',
      },
      title: 'Fuzzy String Example List',
      type: 'array',
    },
    integer_example_list: {
      description: 'A list of simple integer fields',
      examples: [[42, 43]],
      items: {
        type: 'integer',
      },
      title: 'Integer Example List',
      type: 'array',
    },
    float_example_list: {
      description: 'A list of simple float fields',
      examples: [[3.14, 2.71]],
      items: {
        type: 'number',
      },
      title: 'Float Example List',
      type: 'array',
    },
    boolean_example_list: {
      description: 'A list of simple boolean fields',
      examples: [[true, false]],
      items: {
        type: 'boolean',
      },
      title: 'Boolean Example List',
      type: 'array',
    },
    datetime_example_list: {
      description: 'A list of date-time strings in ISO 8601 format',
      examples: [['2023-04-05T14:30:00Z', '2023-04-06T14:30:00Z']],
      items: {
        format: 'date-time',
        type: 'string',
      },
      title: 'Datetime Example List',
      type: 'array',
    },
    datetime_local_example_list: {
      description: 'A list of DateTimeLocal fields',
      items: {
        $ref: '#/$defs/DatetimeLocal',
      },
      title: 'Datetime Local Example List',
      type: 'array',
    },
    email_example_list: {
      description: 'A list of strings formatted as email addresses',
      examples: [['user1@example.com', 'user2@example.com']],
      items: {
        examples: ['john.doe@example.com'],
        format: 'email',
        type: 'string',
      },
      title: 'Email Example List',
      type: 'array',
    },
    html_string_example_list: {
      description: 'A list of HTMLString fields',
      examples: [['<p>HTML text 1</p>', '<p>HTML text 2</p>']],
      items: {
        format: 'html',
        type: 'string',
      },
      title: 'Html String Example List',
      type: 'array',
    },
    enum_example_list: {
      description: 'A list of enumerations with predefined options',
      items: {
        $ref: '#/$defs/EnumExample',
      },
      title: 'Enum Example List',
      type: 'array',
    },
    https_url_example_list: {
      description: 'A list of strings formatted as HTTPS URLs',
      examples: [['https://example1.com', 'https://example2.com']],
      items: {
        examples: ['http://www.example.com'],
        format: 'url',
        type: 'string',
      },
      title: 'Https Url Example List',
      type: 'array',
    },
    dict_example_list: {
      description: 'A list of simple dictionary fields',
      examples: [
        [
          {
            key1: 'value1',
          },
          {
            key2: 'value2',
          },
        ],
      ],
      items: {
        additionalProperties: {
          type: 'string',
        },
        type: 'object',
      },
      title: 'Dict Example List',
      type: 'array',
    },
    nested_object_example_list: {
      description: 'A list of nested object examples',
      items: {
        $ref: '#/$defs/NestedObjectExampleWithImage',
      },
      title: 'Nested Object Example List',
      type: 'array',
    },
    image_example_list: {
      description: 'An image list field',
      items: {
        $ref: '#/$defs/Image',
      },
      title: 'Image Example List',
      type: 'array',
    },
  },
  required: [
    'string_example',
    'fuzzy_string_example',
    'integer_example',
    'float_example',
    'boolean_example',
    'datetime_example',
    'datetime_local_example',
    'email_example',
    'html_string_example',
    'enum_example',
    'https_url_example',
    'time_zone_example',
    'dict_example',
    'nested_object_example',
    'image_example',
    'string_example_list',
    'fuzzy_string_example_list',
    'integer_example_list',
    'float_example_list',
    'boolean_example_list',
    'datetime_example_list',
    'datetime_local_example_list',
    'email_example_list',
    'html_string_example_list',
    'enum_example_list',
    'https_url_example_list',
    'dict_example_list',
    'nested_object_example_list',
    'image_example_list',
  ],
  title: 'DemoAllFieldsTaskInput',
  type: 'object',
};

const splattedEditorFields: SchemaEditorField = {
  fields: [
    {
      description: 'A simple string field',
      examples: ['Sample text'],
      keyName: 'string_example',
      title: 'String Example',
      type: 'string',
    },
    {
      description: 'A fuzzy string field',
      examples: ['Sample fuzzy string'],
      keyName: 'fuzzy_string_example',
      title: 'Fuzzy String Example',
      type: 'string',
    },
    {
      description: 'A simple integer field',
      examples: [42],
      keyName: 'integer_example',
      title: 'Integer Example',
      type: 'integer',
    },
    {
      description: 'A simple float field',
      examples: [3.14],
      keyName: 'float_example',
      title: 'Float Example',
      type: 'number',
    },
    {
      description: 'A simple boolean field',
      examples: [true],
      keyName: 'boolean_example',
      title: 'Boolean Example',
      type: 'boolean',
    },
    {
      description: 'A date-time string in ISO 8601 format',
      examples: ['2023-04-05T14:30:00Z'],
      keyName: 'datetime_example',
      title: 'Datetime Example',
      type: 'date-time',
    },
    {
      description:
        'This class represents a local datetime, with a datetime and a timezone.',
      fields: [
        {
          description: 'The date of the local datetime.',
          examples: ['2023-03-01'],
          keyName: 'date',
          title: 'Date',
          type: 'date',
        },
        {
          description: 'The time of the local datetime without timezone info.',
          examples: ['12:00:00', '22:00:00'],
          keyName: 'local_time',
          title: 'Local Time',
          type: 'time',
        },
        {
          description: 'The timezone of the local time.',
          examples: ['Europe/Paris', 'America/New_York'],
          keyName: 'timezone',
          title: 'Timezone',
          type: 'timezone',
        },
      ],
      keyName: 'datetime_local_example',
      title: 'DatetimeLocal',
      type: 'object',
    },
    {
      description: 'A string formatted as an email address',
      examples: ['user@example.com'],
      keyName: 'email_example',
      title: 'Email Example',
      type: 'string',
    },
    {
      description: 'An HTMLString field',
      examples: ['<p>HTML text</p>'],
      keyName: 'html_string_example',
      title: 'Html String Example',
      type: 'html',
    },
    {
      enum: ['Option1', 'Option2', 'Option3'],
      keyName: 'enum_example',
      title: 'EnumExample',
      type: 'enum',
    },
    {
      description: 'A string formatted as an HTTPS URL',
      examples: ['https://example.com'],
      keyName: 'https_url_example',
      title: 'Https Url Example',
      type: 'string',
    },
    {
      description: 'A string formatted as a time zone',
      examples: ['America/New_York'],
      keyName: 'time_zone_example',
      title: 'Time Zone Example',
      type: 'timezone',
    },
    {
      description: 'A simple dictionary field',
      examples: [{ key: 'value' }],
      fields: [],
      keyName: 'dict_example',
      title: 'Dict Example',
      type: 'object',
    },
    {
      fields: [
        {
          description: 'A simple string field',
          examples: ['Sample text'],
          keyName: 'nested_string_example',
          title: 'Nested String Example',
          type: 'string',
        },
        {
          description: 'A fuzzy string field',
          examples: ['Sample fuzzy string'],
          keyName: 'nested_fuzzy_string_example',
          title: 'Nested Fuzzy String Example',
          type: 'string',
        },
        {
          description: 'A simple integer field',
          examples: [42],
          keyName: 'nested_integer_example',
          title: 'Nested Integer Example',
          type: 'integer',
        },
        {
          description: 'A simple float field',
          examples: [3.14],
          keyName: 'nested_float_example',
          title: 'Nested Float Example',
          type: 'number',
        },
        {
          description: 'A simple boolean field',
          examples: [true],
          keyName: 'nested_boolean_example',
          title: 'Nested Boolean Example',
          type: 'boolean',
        },
        {
          description: 'A date-time string in ISO 8601 format',
          examples: ['2023-04-05T14:30:00Z'],
          keyName: 'nested_datetime_example',
          title: 'Nested Datetime Example',
          type: 'date-time',
        },
        {
          description:
            'This class represents a local datetime, with a datetime and a timezone.',
          fields: [
            {
              description: 'The date of the local datetime.',
              examples: ['2023-03-01'],
              keyName: 'date',
              title: 'Date',
              type: 'date',
            },
            {
              description:
                'The time of the local datetime without timezone info.',
              examples: ['12:00:00', '22:00:00'],
              keyName: 'local_time',
              title: 'Local Time',
              type: 'time',
            },
            {
              description: 'The timezone of the local time.',
              examples: ['Europe/Paris', 'America/New_York'],
              keyName: 'timezone',
              title: 'Timezone',
              type: 'timezone',
            },
          ],
          keyName: 'nested_datetime_local_example',
          title: 'DatetimeLocal',
          type: 'object',
        },
        {
          description: 'A string formatted as an email address',
          examples: ['user@example.com'],
          keyName: 'nested_email_example',
          title: 'Nested Email Example',
          type: 'string',
        },
        {
          description: 'An HTMLString field',
          examples: ['<p>HTML text</p>'],
          keyName: 'nested_html_string_example',
          title: 'Nested Html String Example',
          type: 'html',
        },
        {
          enum: ['Option1', 'Option2', 'Option3'],
          keyName: 'nested_enum_example',
          title: 'EnumExample',
          type: 'enum',
        },
        {
          description: 'A string formatted as an HTTPS URL',
          examples: ['https://example.com'],
          keyName: 'nested_https_url_example',
          title: 'Nested Https Url Example',
          type: 'string',
        },
        {
          description: 'A string formatted as a time zone',
          examples: ['America/New_York'],
          keyName: 'nested_time_zone_example',
          title: 'Nested Time Zone Example',
          type: 'timezone',
        },
        {
          description: 'A simple dictionary field',
          examples: [{ key: 'value' }],
          fields: [],
          keyName: 'nested_dict_example',
          title: 'Nested Dict Example',
          type: 'object',
        },
        {
          keyName: 'nested_image',
          type: 'image',
        },
      ],
      keyName: 'nested_object_example',
      title: 'NestedObjectExampleWithImage',
      type: 'object',
    },
    {
      keyName: 'image_example',
      type: 'image',
    },
    {
      arrayType: 'string',
      description: 'A list of simple string fields',
      examples: [['Sample text 1', 'Sample text 2']],
      fields: [
        {
          keyName: 'string_example_list',
          type: 'string',
        },
      ],
      keyName: 'string_example_list',
      title: 'String Example List',
      type: 'array',
    },
    {
      arrayType: 'string',
      description: 'A list of fuzzy string fields',
      examples: [['Sample fuzzy string 1', 'Sample fuzzy string 2']],
      fields: [
        {
          keyName: 'fuzzy_string_example_list',
          type: 'string',
        },
      ],
      keyName: 'fuzzy_string_example_list',
      title: 'Fuzzy String Example List',
      type: 'array',
    },
    {
      arrayType: 'integer',
      description: 'A list of simple integer fields',
      examples: [[42, 43]],
      fields: [
        {
          keyName: 'integer_example_list',
          type: 'integer',
        },
      ],
      keyName: 'integer_example_list',
      title: 'Integer Example List',
      type: 'array',
    },
    {
      arrayType: 'number',
      description: 'A list of simple float fields',
      examples: [[3.14, 2.71]],
      fields: [
        {
          keyName: 'float_example_list',
          type: 'number',
        },
      ],
      keyName: 'float_example_list',
      title: 'Float Example List',
      type: 'array',
    },
    {
      arrayType: 'boolean',
      description: 'A list of simple boolean fields',
      examples: [[true, false]],
      fields: [
        {
          keyName: 'boolean_example_list',
          type: 'boolean',
        },
      ],
      keyName: 'boolean_example_list',
      title: 'Boolean Example List',
      type: 'array',
    },
    {
      arrayType: 'date-time',
      description: 'A list of date-time strings in ISO 8601 format',
      examples: [['2023-04-05T14:30:00Z', '2023-04-06T14:30:00Z']],
      fields: [
        {
          keyName: 'datetime_example_list',
          type: 'date-time',
        },
      ],
      keyName: 'datetime_example_list',
      title: 'Datetime Example List',
      type: 'array',
    },
    {
      arrayType: 'object',
      description: 'A list of DateTimeLocal fields',
      fields: [
        {
          description: 'The date of the local datetime.',
          examples: ['2023-03-01'],
          keyName: 'date',
          title: 'Date',
          type: 'date',
        },
        {
          description: 'The time of the local datetime without timezone info.',
          examples: ['12:00:00', '22:00:00'],
          keyName: 'local_time',
          title: 'Local Time',
          type: 'time',
        },
        {
          description: 'The timezone of the local time.',
          examples: ['Europe/Paris', 'America/New_York'],
          keyName: 'timezone',
          title: 'Timezone',
          type: 'timezone',
        },
      ],
      keyName: 'datetime_local_example_list',
      title: 'Datetime Local Example List',
      type: 'array',
    },
    {
      arrayType: 'string',
      description: 'A list of strings formatted as email addresses',
      examples: [['user1@example.com', 'user2@example.com']],
      fields: [
        {
          examples: ['john.doe@example.com'],
          keyName: 'email_example_list',
          type: 'string',
        },
      ],
      keyName: 'email_example_list',
      title: 'Email Example List',
      type: 'array',
    },
    {
      arrayType: 'html',
      description: 'A list of HTMLString fields',
      examples: [['<p>HTML text 1</p>', '<p>HTML text 2</p>']],
      fields: [
        {
          keyName: 'html_string_example_list',
          type: 'html',
        },
      ],
      keyName: 'html_string_example_list',
      title: 'Html String Example List',
      type: 'array',
    },
    {
      arrayType: 'enum',
      description: 'A list of enumerations with predefined options',
      fields: [
        {
          enum: ['Option1', 'Option2', 'Option3'],
          keyName: 'enum_example_list',
          title: 'EnumExample',
          type: 'enum',
        },
      ],
      keyName: 'enum_example_list',
      title: 'Enum Example List',
      type: 'array',
    },
    {
      arrayType: 'string',
      description: 'A list of strings formatted as HTTPS URLs',
      examples: [['https://example1.com', 'https://example2.com']],
      fields: [
        {
          examples: ['http://www.example.com'],
          keyName: 'https_url_example_list',
          type: 'string',
        },
      ],
      keyName: 'https_url_example_list',
      title: 'Https Url Example List',
      type: 'array',
    },
    {
      arrayType: 'object',
      description: 'A list of simple dictionary fields',
      examples: [[{ key1: 'value1' }, { key2: 'value2' }]],
      fields: undefined,
      keyName: 'dict_example_list',
      title: 'Dict Example List',
      type: 'array',
    },
    {
      arrayType: 'object',
      description: 'A list of nested object examples',
      fields: [
        {
          description: 'A simple string field',
          examples: ['Sample text'],
          keyName: 'nested_string_example',
          title: 'Nested String Example',
          type: 'string',
        },
        {
          description: 'A fuzzy string field',
          examples: ['Sample fuzzy string'],
          keyName: 'nested_fuzzy_string_example',
          title: 'Nested Fuzzy String Example',
          type: 'string',
        },
        {
          description: 'A simple integer field',
          examples: [42],
          keyName: 'nested_integer_example',
          title: 'Nested Integer Example',
          type: 'integer',
        },
        {
          description: 'A simple float field',
          examples: [3.14],
          keyName: 'nested_float_example',
          title: 'Nested Float Example',
          type: 'number',
        },
        {
          description: 'A simple boolean field',
          examples: [true],
          keyName: 'nested_boolean_example',
          title: 'Nested Boolean Example',
          type: 'boolean',
        },
        {
          description: 'A date-time string in ISO 8601 format',
          examples: ['2023-04-05T14:30:00Z'],
          keyName: 'nested_datetime_example',
          title: 'Nested Datetime Example',
          type: 'date-time',
        },
        {
          description:
            'This class represents a local datetime, with a datetime and a timezone.',
          fields: [
            {
              description: 'The date of the local datetime.',
              examples: ['2023-03-01'],
              keyName: 'date',
              title: 'Date',
              type: 'date',
            },
            {
              description:
                'The time of the local datetime without timezone info.',
              examples: ['12:00:00', '22:00:00'],
              keyName: 'local_time',
              title: 'Local Time',
              type: 'time',
            },
            {
              description: 'The timezone of the local time.',
              examples: ['Europe/Paris', 'America/New_York'],
              keyName: 'timezone',
              title: 'Timezone',
              type: 'timezone',
            },
          ],
          keyName: 'nested_datetime_local_example',
          title: 'DatetimeLocal',
          type: 'object',
        },
        {
          description: 'A string formatted as an email address',
          examples: ['user@example.com'],
          keyName: 'nested_email_example',
          title: 'Nested Email Example',
          type: 'string',
        },
        {
          description: 'An HTMLString field',
          examples: ['<p>HTML text</p>'],
          keyName: 'nested_html_string_example',
          title: 'Nested Html String Example',
          type: 'html',
        },
        {
          enum: ['Option1', 'Option2', 'Option3'],
          keyName: 'nested_enum_example',
          title: 'EnumExample',
          type: 'enum',
        },
        {
          description: 'A string formatted as an HTTPS URL',
          examples: ['https://example.com'],
          keyName: 'nested_https_url_example',
          title: 'Nested Https Url Example',
          type: 'string',
        },
        {
          description: 'A string formatted as a time zone',
          examples: ['America/New_York'],
          keyName: 'nested_time_zone_example',
          title: 'Nested Time Zone Example',
          type: 'timezone',
        },
        {
          description: 'A simple dictionary field',
          examples: [{ key: 'value' }],
          fields: [],
          keyName: 'nested_dict_example',
          title: 'Nested Dict Example',
          type: 'object',
        },
        {
          keyName: 'nested_image',
          type: 'image',
        },
      ],
      keyName: 'nested_object_example_list',
      title: 'Nested Object Example List',
      type: 'array',
    },
    {
      arrayType: 'image',
      description: 'An image list field',
      fields: undefined,
      keyName: 'image_example_list',
      title: 'Image Example List',
      type: 'array',
    },
  ],
  keyName: '',
  title: 'DemoAllFieldsTaskInput',
  type: 'object',
};

const finalSchema: JsonObjectSchema = {
  properties: {
    boolean_example: {
      description: 'A simple boolean field',
      examples: [true],
      title: 'Boolean Example',
      type: 'boolean',
    },
    boolean_example_list: {
      description: 'A list of simple boolean fields',
      examples: [[true, false]],
      items: {
        type: 'boolean',
      },
      title: 'Boolean Example List',
      type: 'array',
    },
    datetime_example: {
      description: 'A date-time string in ISO 8601 format',
      examples: ['2023-04-05T14:30:00Z'],
      format: 'date-time',
      title: 'Datetime Example',
      type: 'string',
    },
    datetime_example_list: {
      description: 'A list of date-time strings in ISO 8601 format',
      examples: [['2023-04-05T14:30:00Z', '2023-04-06T14:30:00Z']],
      items: {
        format: 'date-time',
        type: 'string',
      },
      title: 'Datetime Example List',
      type: 'array',
    },
    datetime_local_example: {
      description:
        'This class represents a local datetime, with a datetime and a timezone.',
      properties: {
        date: {
          description: 'The date of the local datetime.',
          examples: ['2023-03-01'],
          format: 'date',
          title: 'Date',
          type: 'string',
        },
        local_time: {
          description: 'The time of the local datetime without timezone info.',
          examples: ['12:00:00', '22:00:00'],
          format: 'time',
          title: 'Local Time',
          type: 'string',
        },
        timezone: {
          description: 'The timezone of the local time.',
          examples: ['Europe/Paris', 'America/New_York'],
          format: 'timezone',
          title: 'Timezone',
          type: 'string',
        },
      },
      title: 'DatetimeLocal',
      type: 'object',
    },
    datetime_local_example_list: {
      description: 'A list of DateTimeLocal fields',
      items: {
        properties: {
          date: {
            description: 'The date of the local datetime.',
            examples: ['2023-03-01'],
            format: 'date',
            title: 'Date',
            type: 'string',
          },
          local_time: {
            description:
              'The time of the local datetime without timezone info.',
            examples: ['12:00:00', '22:00:00'],
            format: 'time',
            title: 'Local Time',
            type: 'string',
          },
          timezone: {
            description: 'The timezone of the local time.',
            examples: ['Europe/Paris', 'America/New_York'],
            format: 'timezone',
            title: 'Timezone',
            type: 'string',
          },
        },
        type: 'object',
      },
      title: 'Datetime Local Example List',
      type: 'array',
    },
    dict_example: {
      description: 'A simple dictionary field',
      examples: [{ key: 'value' }],
      properties: {},
      title: 'Dict Example',
      type: 'object',
    },
    dict_example_list: {
      description: 'A list of simple dictionary fields',
      examples: [[{ key1: 'value1' }, { key2: 'value2' }]],
      items: {},
      title: 'Dict Example List',
      type: 'array',
    },
    email_example: {
      description: 'A string formatted as an email address',
      examples: ['user@example.com'],
      title: 'Email Example',
      type: 'string',
    },
    email_example_list: {
      description: 'A list of strings formatted as email addresses',
      examples: [['user1@example.com', 'user2@example.com']],
      items: {
        examples: ['john.doe@example.com'],
        type: 'string',
      },
      title: 'Email Example List',
      type: 'array',
    },
    enum_example: {
      enum: ['Option1', 'Option2', 'Option3'],
      title: 'EnumExample',
      type: 'string',
    },
    enum_example_list: {
      description: 'A list of enumerations with predefined options',
      items: {
        enum: ['Option1', 'Option2', 'Option3'],
        title: 'EnumExample',
        type: 'string',
      },
      title: 'Enum Example List',
      type: 'array',
    },
    float_example: {
      description: 'A simple float field',
      examples: [3.14],
      title: 'Float Example',
      type: 'number',
    },
    float_example_list: {
      description: 'A list of simple float fields',
      examples: [[3.14, 2.71]],
      items: {
        type: 'number',
      },
      title: 'Float Example List',
      type: 'array',
    },
    fuzzy_string_example: {
      description: 'A fuzzy string field',
      examples: ['Sample fuzzy string'],
      title: 'Fuzzy String Example',
      type: 'string',
    },
    fuzzy_string_example_list: {
      description: 'A list of fuzzy string fields',
      examples: [['Sample fuzzy string 1', 'Sample fuzzy string 2']],
      items: {
        type: 'string',
      },
      title: 'Fuzzy String Example List',
      type: 'array',
    },
    html_string_example: {
      description: 'An HTMLString field',
      examples: ['<p>HTML text</p>'],
      format: 'html',
      title: 'Html String Example',
      type: 'string',
    },
    html_string_example_list: {
      description: 'A list of HTMLString fields',
      examples: [['<p>HTML text 1</p>', '<p>HTML text 2</p>']],
      items: {
        format: 'html',
        type: 'string',
      },
      title: 'Html String Example List',
      type: 'array',
    },
    https_url_example: {
      description: 'A string formatted as an HTTPS URL',
      examples: ['https://example.com'],
      title: 'Https Url Example',
      type: 'string',
    },
    https_url_example_list: {
      description: 'A list of strings formatted as HTTPS URLs',
      examples: [['https://example1.com', 'https://example2.com']],
      items: {
        examples: ['http://www.example.com'],
        type: 'string',
      },
      title: 'Https Url Example List',
      type: 'array',
    },
    image_example: {
      $ref: '#/$defs/Image',
    },
    image_example_list: {
      description: 'An image list field',
      items: {
        $ref: '#/$defs/Image',
      },
      title: 'Image Example List',
      type: 'array',
    },
    integer_example: {
      description: 'A simple integer field',
      examples: [42],
      title: 'Integer Example',
      type: 'integer',
    },
    integer_example_list: {
      description: 'A list of simple integer fields',
      examples: [[42, 43]],
      items: {
        type: 'integer',
      },
      title: 'Integer Example List',
      type: 'array',
    },
    nested_object_example: {
      properties: {
        nested_boolean_example: {
          description: 'A simple boolean field',
          examples: [true],
          title: 'Nested Boolean Example',
          type: 'boolean',
        },
        nested_datetime_example: {
          description: 'A date-time string in ISO 8601 format',
          examples: ['2023-04-05T14:30:00Z'],
          format: 'date-time',
          title: 'Nested Datetime Example',
          type: 'string',
        },
        nested_datetime_local_example: {
          description:
            'This class represents a local datetime, with a datetime and a timezone.',
          properties: {
            date: {
              description: 'The date of the local datetime.',
              examples: ['2023-03-01'],
              format: 'date',
              title: 'Date',
              type: 'string',
            },
            local_time: {
              description:
                'The time of the local datetime without timezone info.',
              examples: ['12:00:00', '22:00:00'],
              format: 'time',
              title: 'Local Time',
              type: 'string',
            },
            timezone: {
              description: 'The timezone of the local time.',
              examples: ['Europe/Paris', 'America/New_York'],
              format: 'timezone',
              title: 'Timezone',
              type: 'string',
            },
          },
          title: 'DatetimeLocal',
          type: 'object',
        },
        nested_dict_example: {
          description: 'A simple dictionary field',
          examples: [{ key: 'value' }],
          title: 'Nested Dict Example',
          properties: {},
          type: 'object',
        },
        nested_email_example: {
          description: 'A string formatted as an email address',
          examples: ['user@example.com'],
          title: 'Nested Email Example',
          type: 'string',
        },
        nested_enum_example: {
          enum: ['Option1', 'Option2', 'Option3'],
          title: 'EnumExample',
          type: 'string',
        },
        nested_float_example: {
          description: 'A simple float field',
          examples: [3.14],
          title: 'Nested Float Example',
          type: 'number',
        },
        nested_fuzzy_string_example: {
          description: 'A fuzzy string field',
          examples: ['Sample fuzzy string'],
          title: 'Nested Fuzzy String Example',
          type: 'string',
        },
        nested_html_string_example: {
          description: 'An HTMLString field',
          examples: ['<p>HTML text</p>'],
          format: 'html',
          title: 'Nested Html String Example',
          type: 'string',
        },
        nested_https_url_example: {
          description: 'A string formatted as an HTTPS URL',
          examples: ['https://example.com'],
          title: 'Nested Https Url Example',
          type: 'string',
        },
        nested_image: {
          $ref: '#/$defs/Image',
        },
        nested_integer_example: {
          description: 'A simple integer field',
          examples: [42],
          title: 'Nested Integer Example',
          type: 'integer',
        },
        nested_string_example: {
          description: 'A simple string field',
          examples: ['Sample text'],
          title: 'Nested String Example',
          type: 'string',
        },
        nested_time_zone_example: {
          description: 'A string formatted as a time zone',
          examples: ['America/New_York'],
          format: 'timezone',
          title: 'Nested Time Zone Example',
          type: 'string',
        },
      },
      title: 'NestedObjectExampleWithImage',
      type: 'object',
    },
    nested_object_example_list: {
      description: 'A list of nested object examples',
      items: {
        properties: {
          nested_boolean_example: {
            description: 'A simple boolean field',
            examples: [true],
            title: 'Nested Boolean Example',
            type: 'boolean',
          },
          nested_datetime_example: {
            description: 'A date-time string in ISO 8601 format',
            examples: ['2023-04-05T14:30:00Z'],
            format: 'date-time',
            title: 'Nested Datetime Example',
            type: 'string',
          },
          nested_datetime_local_example: {
            description:
              'This class represents a local datetime, with a datetime and a timezone.',
            properties: {
              date: {
                description: 'The date of the local datetime.',
                examples: ['2023-03-01'],
                format: 'date',
                title: 'Date',
                type: 'string',
              },
              local_time: {
                description:
                  'The time of the local datetime without timezone info.',
                examples: ['12:00:00', '22:00:00'],
                format: 'time',
                title: 'Local Time',
                type: 'string',
              },
              timezone: {
                description: 'The timezone of the local time.',
                examples: ['Europe/Paris', 'America/New_York'],
                format: 'timezone',
                title: 'Timezone',
                type: 'string',
              },
            },
            title: 'DatetimeLocal',
            type: 'object',
          },
          nested_dict_example: {
            description: 'A simple dictionary field',
            examples: [{ key: 'value' }],
            title: 'Nested Dict Example',
            properties: {},
            type: 'object',
          },
          nested_email_example: {
            description: 'A string formatted as an email address',
            examples: ['user@example.com'],
            title: 'Nested Email Example',
            type: 'string',
          },
          nested_enum_example: {
            enum: ['Option1', 'Option2', 'Option3'],
            title: 'EnumExample',
            type: 'string',
          },
          nested_float_example: {
            description: 'A simple float field',
            examples: [3.14],
            title: 'Nested Float Example',
            type: 'number',
          },
          nested_fuzzy_string_example: {
            description: 'A fuzzy string field',
            examples: ['Sample fuzzy string'],
            title: 'Nested Fuzzy String Example',
            type: 'string',
          },
          nested_html_string_example: {
            description: 'An HTMLString field',
            examples: ['<p>HTML text</p>'],
            format: 'html',
            title: 'Nested Html String Example',
            type: 'string',
          },
          nested_https_url_example: {
            description: 'A string formatted as an HTTPS URL',
            examples: ['https://example.com'],
            title: 'Nested Https Url Example',
            type: 'string',
          },
          nested_image: {
            $ref: '#/$defs/Image',
          },
          nested_integer_example: {
            description: 'A simple integer field',
            examples: [42],
            title: 'Nested Integer Example',
            type: 'integer',
          },
          nested_string_example: {
            description: 'A simple string field',
            examples: ['Sample text'],
            title: 'Nested String Example',
            type: 'string',
          },
          nested_time_zone_example: {
            description: 'A string formatted as a time zone',
            examples: ['America/New_York'],
            format: 'timezone',
            title: 'Nested Time Zone Example',
            type: 'string',
          },
        },
        type: 'object',
      },
      title: 'Nested Object Example List',
      type: 'array',
    },
    string_example: {
      description: 'A simple string field',
      examples: ['Sample text'],
      title: 'String Example',
      type: 'string',
    },
    string_example_list: {
      description: 'A list of simple string fields',
      examples: [['Sample text 1', 'Sample text 2']],
      items: {
        type: 'string',
      },
      title: 'String Example List',
      type: 'array',
    },
    time_zone_example: {
      description: 'A string formatted as a time zone',
      examples: ['America/New_York'],
      format: 'timezone',
      title: 'Time Zone Example',
      type: 'string',
    },
  },
  title: 'DemoAllFieldsTaskInput',
  type: 'object',
};

export const refObjectsSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema,
};

export const refObjectDefinitionFixtures = {
  originalDefinitions: unionObjectsOriginalDefinitions,
  finalDefinitions: {},
};
