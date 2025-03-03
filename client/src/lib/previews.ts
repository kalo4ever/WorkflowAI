import { GeneralizedTaskInput } from '@/types';
import { SchemaNodeType } from './schemaUtils';

class MaxLenReached extends Error {}

class Agg {
  agg: string[];
  remaining: number;

  constructor(remaining: number) {
    this.agg = [];
    this.remaining = remaining;
  }

  private stringify(value: string | number | boolean | null): string {
    if (typeof value === 'number' && !Number.isInteger(value)) {
      return value.toFixed(2).replace(/0+$/, '').replace(/\.$/, '');
    }
    if (value === null) {
      return 'null';
    }
    if (typeof value === 'boolean') {
      return value ? 'true' : 'false';
    }
    return String(value).replace('\n', ' ');
  }

  append(val: string | number | boolean | null): void {
    const s = this.stringify(val);
    if (this.remaining < s.length) {
      this.agg.push(s.slice(0, this.remaining));
      throw new MaxLenReached();
    }
    this.agg.push(s);
    this.remaining -= s.length;
    if (this.remaining === 0) {
      throw new MaxLenReached();
    }
  }

  toString(): string {
    return this.agg.join('');
  }
}

function anyPreview(value: SchemaNodeType, agg: Agg): void {
  if (
    typeof value === 'object' &&
    !Array.isArray(value) &&
    value !== null &&
    !(value instanceof Date)
  ) {
    agg.append('{');
    // eslint-disable-next-line no-use-before-define -- recursive call
    dictPreview(value, agg);
    agg.append('}');
  } else if (Array.isArray(value)) {
    agg.append('[');
    // eslint-disable-next-line no-use-before-define -- recursive call
    listPreview(value as SchemaNodeType[], agg);
    agg.append(']');
  } else if (typeof value === 'string') {
    agg.append(`"${value}"`);
    // check if value is a Date
  } else if (value instanceof Date) {
    agg.append(value.toISOString());
  } else {
    agg.append(value);
  }
}

function dictPreview(d: Record<string, unknown>, agg: Agg): void {
  const entries = Object.entries(d);
  for (let i = 0; i < entries.length; i++) {
    const [k, v] = entries[i];
    if (i > 0) {
      agg.append(', ');
    }
    agg.append(k);
    agg.append(': ');
    anyPreview(v as SchemaNodeType, agg);
  }
}

function listPreview(arr: SchemaNodeType[], agg: Agg): void {
  for (let i = 0; i < arr.length; i++) {
    if (i > 0) {
      agg.append(', ');
    }
    anyPreview(arr[i], agg);
  }
}

export function computePreview(
  input: GeneralizedTaskInput | null | undefined,
  maxLen: number = 200
): string {
  if (!input) {
    return '-';
  }

  const agg = new Agg(maxLen);
  try {
    if (typeof input === 'object' && !Array.isArray(input) && input !== null) {
      dictPreview(input, agg);
    } else if (Array.isArray(input)) {
      listPreview(input, agg);
    } else {
      agg.append(input);
    }
  } catch (e) {
    if (!(e instanceof MaxLenReached)) {
      throw e;
    }
  }
  return agg.toString();
}
