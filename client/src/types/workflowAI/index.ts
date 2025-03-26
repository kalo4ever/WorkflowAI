import { TaskGroupProperties_Output, VersionV1 as _VersionV1 } from './models';

export * from './models';

export interface VersionV1Properties extends TaskGroupProperties_Output {
  task_variant_id?: string | null;
}

export type VersionV1 = Omit<_VersionV1, 'properties' | 'input_schema' | 'output_schema'> & {
  properties: VersionV1Properties;
  input_schema?: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
};
