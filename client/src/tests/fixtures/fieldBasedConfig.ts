import { FieldEvaluationOptions, ObjectKeyType } from '@/lib/schemaUtils';
import { JsonSchema } from '@/types';

const outputSchema: JsonSchema = {
  type: 'object',
  properties: {
    processed_string: {
      description: 'Processed string output',
      examples: ['Processed example string'],
      type: 'string',
    },
    calculated_number: {
      description: 'A calculated number based on input',
      examples: [84],
      type: 'number',
    },
    is_valid: {
      description: 'A boolean indicating if the input is valid',
      type: 'boolean',
    },
    processed_array: {
      description: 'A processed array of numbers',
      type: 'array',
      items: {
        type: 'number',
      },
    },
    summary_object: {
      description: 'A summary object of the input',
      type: 'object',
      properties: {
        total_fields: {
          description: 'Total number of fields in the input',
          examples: [11],
          type: 'number',
        },
        has_image: {
          description: 'Indicates if an image was provided in the input',
          type: 'boolean',
        },
      },
    },
    selected_option: {
      description: 'The selected option from the enum field',
      enum: ['OPTION_A', 'OPTION_B', 'OPTION_C', 'OTHER'],
      type: 'string',
    },
    formatted_date: {
      description: 'A formatted date string based on the input date-time',
      examples: ['2023-05-15'],
      type: 'string',
    },
  },
  $defs: {},
};

const originalOutput: Record<string, unknown> = {
  processed_string: 'Processed Innovative string content',
  calculated_number: 95.78,
  is_valid: true,
  processed_array: [5, 4, 5],
  summary_object: {
    total_fields: 11,
    has_image: true,
  },
  selected_option: 'OPTION_C',
  formatted_date: '2025-06-15',
};

const flatFieldBasedConfig: ObjectKeyType[] = [
  {
    path: '',
    type: 'object',
    value: FieldEvaluationOptions.STRICTLY_EQUAL,
  },
  {
    path: 'processed_string',
    type: 'string',
    value: FieldEvaluationOptions.SOFT_EQUAL,
  },
  {
    path: 'calculated_number',
    type: 'number',
    value: FieldEvaluationOptions.STRICTLY_EQUAL,
  },
  {
    path: 'is_valid',
    type: 'boolean',
    value: FieldEvaluationOptions.STRICTLY_EQUAL,
  },
  {
    path: 'processed_array',
    type: 'array',
    value: FieldEvaluationOptions.FLEXIBLE_ORDERING,
  },
  {
    path: 'processed_array.0',
    type: 'number',
    value: FieldEvaluationOptions.STRICTLY_EQUAL,
  },
  {
    path: 'summary_object',
    type: 'object',
    value: FieldEvaluationOptions.STRICTLY_EQUAL,
  },
  {
    path: 'summary_object.total_fields',
    type: 'number',
    value: FieldEvaluationOptions.STRICTLY_EQUAL,
  },
  {
    path: 'summary_object.has_image',
    type: 'boolean',
    value: FieldEvaluationOptions.STRICTLY_EQUAL,
  },
  {
    path: 'selected_option',
    type: 'string',
    value: FieldEvaluationOptions.STRICTLY_EQUAL,
  },
  {
    path: 'formatted_date',
    type: 'string',
    value: FieldEvaluationOptions.SOFT_EQUAL,
  },
];

export const fieldBasedConfigFixtures = {
  outputSchema,
  originalOutput,
  flatFieldBasedConfig,
};
