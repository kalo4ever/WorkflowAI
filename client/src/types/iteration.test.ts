import { parseGroupIteration } from './iteration';

describe('parseGroupIteration', () => {
  it('should return undefined for undefined', () => {
    expect(parseGroupIteration(undefined)).toBeUndefined();
  });

  it('should return undefined for empty string', () => {
    expect(parseGroupIteration('')).toBeUndefined();
  });

  it('should return undefined for NaN', () => {
    expect(parseGroupIteration('bla')).toBeUndefined();
  });

  it('should return the number for a valid number', () => {
    expect(parseGroupIteration('123')).toBe(123);
  });

  it('should return undefined for 0', () => {
    expect(parseGroupIteration('0')).toBeUndefined();
  });
});
