import {
  FieldFilter,
  Operator,
  deserializeFieldFilter,
  serializeFieldFilter,
} from './operator';

describe('field filters', () => {
  const cases: [FieldFilter, string][] = [
    [{ keypath: 'a', operator: Operator.eq, value: 1 }, 'a[=]1'],
    [{ keypath: 'a.b', operator: Operator.eq, value: 1 }, 'a.b[=]1'],
    [{ keypath: 'a', operator: Operator.ne, value: 'he llo' }, 'a[!=]"he llo"'],
    [{ keypath: 'a', operator: Operator.in, value: [1, 2] }, 'a[in][1,2]'],
  ];

  describe('serializeFieldFilter', () => {
    it.each(cases)('should serialize %j to %s', (filter, expected) => {
      expect(serializeFieldFilter(filter)).toBe(expected);
    });
  });
  describe('deserializeFieldFilter', () => {
    it.each(cases)('should deserialize %s to %j', (expected, filter) => {
      expect(deserializeFieldFilter(filter)).toEqual(expected);
    });
  });
});
