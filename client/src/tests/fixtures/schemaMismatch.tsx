import { SerializableTaskIOWithSchema } from '@/types/task';

// Here we test the case where the schema and the task output do not match
export const schemaMismatch: {
  taskOutput: Record<string, unknown>;
  taskSchema: SerializableTaskIOWithSchema;
} = {
  taskOutput: {
    status: {
      coding: [
        {
          code: 'B',
        },
      ],
    },
  },
  taskSchema: {
    version: 'f8fe795d2024d7cdc3fde658569757bd',
    json_schema: {
      $defs: {},
      properties: {
        status: {
          description: 'a simple status',
          enum: [
            'BILLED',
            'BILLABLE',
            'PLANNED',
            'NOT_BILLABLE',
            'ABORTED',
            'ENTERED_IN_ERROR',
            'UNKNOWN',
          ],
          title: 'LineItemStatus',
          type: 'string',
        },
      },
      required: ['status'],
      title: 'MedicalBillExtractTaskOutput',
      type: 'object',
    },
  },
};
