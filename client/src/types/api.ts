import { FieldFilter } from './operator';

export interface TaskRunQuery {
  has_scores?: boolean;
  has_example?: boolean;
  group_iterations?: string[];
  fields?: FieldFilter[];
  score_filters?: string[];
}
