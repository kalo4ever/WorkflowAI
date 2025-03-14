export function parseGroupIteration(
  value: string | undefined
): number | undefined {
  // Ok for falsy check here, 0 or '' or null should always be undefined
  // There is no iteration 0
  if (!value) return undefined;
  const parsedValue = parseInt(value);
  // if the value is falsy again, return undefined
  return parsedValue || undefined;
}
