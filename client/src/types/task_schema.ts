import { JsonSchema } from './json_schema';

export interface TaskIO {
  _id: string;
  name: string;
  version: string;
  created_at: Date;
  json_schema: JsonSchema;
}
