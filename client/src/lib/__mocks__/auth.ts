export const GET = jest.fn();
export const POST = jest.fn();
export function auth(
  fn: (...args: unknown[]) => unknown
): (...args: unknown[]) => unknown {
  return fn;
}
