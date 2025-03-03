export interface QueryFieldMapper<V> {
  get(params: URLSearchParams, key: string): V;
  set(params: URLSearchParams, key: string, val: V): void;
}

const queryStringMapper: QueryFieldMapper<string | undefined> = {
  get(params, key) {
    return params.get(key) || undefined;
  },
  set(params, key, val) {
    if (val === undefined) {
      params.delete(key);
    } else {
      params.set(key, val);
    }
  },
};

const queryNumberMapper: QueryFieldMapper<number | undefined> = {
  get(params, key) {
    return Number(params.get(key)) || undefined;
  },
  set(params, key, val) {
    if (val === undefined) {
      params.delete(key);
    } else {
      params.set(key, val.toString());
    }
  },
};

const queryBooleanMapper: QueryFieldMapper<boolean | undefined> = {
  get(params, key) {
    const val = params.get(key);
    if (val === 'true') {
      return true;
    } else if (val === 'false') {
      return false;
    }
    return undefined;
  },
  set(params, key, val) {
    if (val === undefined) {
      params.delete(key);
    } else {
      params.set(key, val.toString());
    }
  },
};

const queryDateMapper: QueryFieldMapper<Date | undefined> = {
  get(params, key) {
    const val = params.get(key);
    return val ? new Date(val) : undefined;
  },
  set(params, key, val) {
    if (val === undefined) {
      params.delete(key);
    } else {
      params.set(key, val.toISOString());
    }
  },
};

const queryDateWithMSMapper: QueryFieldMapper<Date | undefined> = {
  get(params, key) {
    const val = params.get(key);
    return val ? new Date(Number(val)) : undefined;
  },
  set(params, key, val) {
    if (!val) {
      params.delete(key);
    } else {
      params.set(key, val.getTime().toString());
    }
  },
};

const stringArrayMapper: QueryFieldMapper<string[]> = {
  get(params, key) {
    return params.getAll(key);
  },
  set(params, key, val) {
    if (val?.length) {
      params.delete(key);
      val.forEach((v) => params.append(key, v));
    } else {
      params.delete(key);
    }
  },
};

const booleanArrayMapper: QueryFieldMapper<boolean[]> = {
  get(params, key) {
    return params.getAll(key).map((v) => v === 'true');
  },
  set(params, key, val) {
    params.delete(key);
    val.forEach((v) => params.append(key, `${v}`));
  },
};

export const mappers = {
  string: queryStringMapper,
  number: queryNumberMapper,
  boolean: queryBooleanMapper,
  date: queryDateMapper,
  dataWithMS: queryDateWithMSMapper,
  strings: stringArrayMapper,
  booleans: booleanArrayMapper,
};

export type QueryMapper<T> = { [K in keyof T]: QueryFieldMapper<T[K]> };

export function mapQuery<T>(val: T, mapper: QueryMapper<T>): URLSearchParams {
  const params = new URLSearchParams();
  for (const key in val) {
    const fieldMapper = mapper[key as keyof T];
    fieldMapper.set(params, key, val[key]);
  }
  return params;
}

export function parseQuery<T>(
  params: URLSearchParams,
  mapper: QueryMapper<T>
): T {
  const parsed = {} as Record<string, unknown>;
  for (const key in mapper) {
    const fieldMapper = mapper[key];
    parsed[key] = fieldMapper.get(params, key);
  }
  return parsed as T;
}
