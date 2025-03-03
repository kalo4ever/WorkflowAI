import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useCallback, useMemo } from 'react';
import { useStableValue } from '../useStable';
import { QueryMapper, mapQuery, parseQuery } from './utils';

// TODO: test
export function useQuery<T>(
  mapper: QueryMapper<T>
): [T, (vals: Partial<T>, extraParams?: Record<string, string>) => void] {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const parsed = useMemo(() => parseQuery(params, mapper), [params, mapper]);
  const stableParsed = useStableValue(parsed);

  const setter = useCallback(
    // extraParams gives us a way to pass frontend params to the query string
    (vals: Partial<T>, extraParams?: Record<string, string>) => {
      const newParams = mapQuery(vals, mapper);
      if (extraParams) {
        Object.entries(extraParams).forEach(([key, value]) => {
          newParams.set(key, value);
        });
      }
      router.replace(`${pathname}?${newParams.toString()}`);
    },
    [mapper, router, pathname]
  );

  return [stableParsed, setter];
}
