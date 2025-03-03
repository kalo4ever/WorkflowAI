import {
  TaskGroupProperties_Output,
  RunItemV1 as _RunItemV1,
  RunV1 as _RunV1,
  VersionV1 as _VersionV1,
} from './models';

export * from './models';

// Override the version of RunItemV1 to account for different version types
export type RunItemV1 = Omit<_RunItemV1, 'version'> & {
  version: {
    id: string;
  };
};

export type RunV1 = Omit<_RunV1, 'version'> & {
  version: {
    id: string;
  };
};

export interface VersionV1Properties extends TaskGroupProperties_Output {
  task_variant_id?: string | null;
}

export type VersionV1 = Omit<_VersionV1, 'properties'> & {
  properties: VersionV1Properties;
};
