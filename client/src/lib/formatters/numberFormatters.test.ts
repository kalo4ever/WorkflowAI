import { formatCurrency, formatFractionalCurrency } from './numberFormatters';

describe('@/lib/formatters/numberFormatters', () => {
  describe('#formatFractionalCurrency', () => {
    const usd = (num: number | null | undefined) => formatFractionalCurrency(num);

    it('is null when the value is not a number', () => {
      expect(usd(undefined)).toEqual(null);
      expect(usd(null)).toEqual(null);
    });

    it('uses a minimum of 4 fractional digits when the value is >= 0.0001', () => {
      expect(usd(1)).toEqual('$1.0000');
      expect(usd(0.02)).toEqual('$0.0200');
      expect(usd(0.0002)).toEqual('$0.0002');
      expect(usd(0.0001)).toEqual('$0.0001');

      expect(usd(0.1234567)).toEqual('$0.1235');
      expect(usd(0.01234567)).toEqual('$0.0123');
      expect(usd(0.001234567)).toEqual('$0.0012');
      expect(usd(0.0001234567)).toEqual('$0.0001');
    });

    it('uses 1 significant digits when the value is less than 0.0001', () => {
      expect(usd(0.00001234567)).toEqual('$0.00001');
      expect(usd(0.000001234567)).toEqual('$0.000001');

      expect(usd(0.00002)).toEqual('$0.00002');
      expect(usd(0.0000029)).toEqual('$0.000003');
      expect(usd(0.0000000000002)).toEqual('$0.0000000000002');
      expect(usd(0.0000000000002109109)).toEqual('$0.0000000000002');
      expect(usd(0.020000001)).toEqual('$0.0200');
    });
  });
  describe('#formatCurrency', () => {
    const usd = (num: number | null | undefined) => formatCurrency(num);

    it('is null when the value is not a number', () => {
      expect(usd(undefined)).toEqual(null);
      expect(usd(null)).toEqual(null);
    });

    expect(usd(1)).toEqual('$1.00');
    expect(usd(0.02)).toEqual('$0.02');
    expect(usd(0.0002)).toEqual('$0.00');
    expect(usd(0.0001)).toEqual('$0.00');
    expect(usd(0.1234567)).toEqual('$0.12');
    expect(usd(0.01234567)).toEqual('$0.01');
    expect(usd(0.001234567)).toEqual('$0.00');
  });
});
