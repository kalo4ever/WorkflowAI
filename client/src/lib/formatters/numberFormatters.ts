export function formatFractionalCurrency(value: number | null | undefined) {
  if (typeof value !== 'number') {
    return null;
  }

  if (Math.abs(value) >= 0.0001) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4,
      maximumFractionDigits: 4,
    }).format(value);
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumSignificantDigits: 1,
    maximumSignificantDigits: 1,
  }).format(value);
}

export function formatCurrency(value: number | null | undefined) {
  if (typeof value !== 'number') {
    return null;
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatNumber(value: number | null | undefined) {
  if (typeof value !== 'number') {
    return null;
  }

  return new Intl.NumberFormat('en-US').format(value);
}
