import { JsonSchema } from './json_schema';
import { TaskSchemaResponse } from './workflowAI/models';

/**
 * A Task represents a unit of work of the AI
 * It is defined by a name and the type of input and output it handles
 */
export interface Task {
  _id: string;
  version: string;
  name: string;
  input_class_id: string;
  output_class_id: string;
}

export type SerializableTaskIOWithSchema = {
  /**
   * the version of the schema definition. Titles and descriptions are ignored.
   */
  version: string;
  /**
   * A json schema
   */
  json_schema: JsonSchema;
};

export type TaskSchemaResponseWithSchema = Omit<TaskSchemaResponse, 'input_schema' | 'output_schema'> & {
  input_schema: SerializableTaskIOWithSchema;
  output_schema: SerializableTaskIOWithSchema;
};
