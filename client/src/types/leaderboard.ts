import { TaskID, TaskSchemaID, TenantID } from './aliases';

export enum LeaderboardCategory {
  EntityExtraction = 'entity-extraction',
  Classification = 'classification',
  Reasoning = 'reasoning',
  ImageAnalysis = 'image-analysis',
}

export interface LeaderboardTaskEntry {
  readonly tenantId: TenantID;
  readonly taskId: TaskID;
  readonly schemaId: TaskSchemaID;
}
