export enum Operator {
  eq = '=',
  ne = '!=',
  gt = '>',
  gte = '>=',
  lt = '<',
  lte = '<=',
  in = 'in',
  nin = 'nin',
}

export interface FieldFilter {
  keypath: string;
  operator: Operator;
  value: unknown;
}

const keypathRegex = /([a-zA-Z0-9_]+)(\.[a-zA-Z0-9_]+)*/;
const serializedRegex = /([a-zA-Z0-9_\-\.]+)\[([^\]]+)\](.*)/;

export class FieldFilterError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'FieldFilterError';
  }
}

export function serializeFieldFilter(filter: FieldFilter): string {
  if (!keypathRegex.test(filter.keypath)) {
    throw new FieldFilterError(`Invalid keypath: ${filter.keypath}`);
  }
  return `${filter.keypath}[${filter.operator}]${JSON.stringify(filter.value)}`;
}

export function deserializeFieldFilter(filter: string): FieldFilter {
  const match = serializedRegex.exec(filter);
  if (!match) {
    throw new FieldFilterError(`Invalid filter: ${filter}`);
  }
  const [, keypath, operator, value] = match;
  return {
    keypath,
    operator: operator as Operator,
    value: JSON.parse(value),
  };
}
