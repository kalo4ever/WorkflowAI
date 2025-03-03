import { Branded } from './utils';

export type TenantID = Branded<string, 'TenandID'>;
export type TaskID = Branded<string, 'TaskID'>;
export type TaskSchemaID = Branded<string, 'TaskSchemaID'>;

export type Model = Branded<string, 'Model'>;
export type ModelOptional = Model | null | undefined;

export const UNDEFINED_MODEL = '' as Model;
