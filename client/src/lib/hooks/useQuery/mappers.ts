import { QueryFieldMapper, QueryMapper, mappers } from '@/lib/hooks/useQuery/utils';
import { type FieldFilter, type TaskRunQuery, deserializeFieldFilter, serializeFieldFilter } from '@/types';

export interface PageTokenQuery {
  page_token?: Date;
}

const fieldFilterMapper: QueryFieldMapper<FieldFilter[]> = {
  get(params, key) {
    return params.getAll(key).map((v) => deserializeFieldFilter(v));
  },
  set(params, key, val) {
    params.delete(key);
    val.forEach((v) => params.append(key, serializeFieldFilter(v)));
  },
};

export const taskRunQueryMapper: QueryMapper<TaskRunQuery> = {
  has_scores: mappers.boolean,
  has_example: mappers.boolean,
  group_iterations: mappers.strings,
  fields: fieldFilterMapper,
  score_filters: mappers.strings,
};
