import { size } from 'lodash';
import { debounce } from 'lodash';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useCallback, useMemo } from 'react';
import { useIsMounted } from 'usehooks-ts';

export type QueryParam =
  | string
  | number
  | boolean
  | string[]
  | undefined
  | null;

export const parseQueryParam = (
  search: string,
  key: string
): string | undefined => {
  const searchParams = new URLSearchParams(search);
  return searchParams.get(key) || undefined;
};

export const parseQueryParams = (search: string): Record<string, string> => {
  const searchParams = new URLSearchParams(search);
  const parsedParams: Record<string, string> = {};
  searchParams.forEach((value, key) => {
    parsedParams[key] = value;
  });
  return parsedParams;
};

export const stringifyQueryParams = (
  params: Record<string, QueryParam> | null | undefined
): string => {
  if (!params || size(params) === 0) {
    return '';
  }

  // We stringify nested objects
  const newParams: Record<string, string> = {};
  Object.entries(params).forEach(([key, value]) => {
    let entry: string | undefined;

    if (typeof value === 'number' || typeof value === 'boolean') {
      entry = String(value);
    } else if (value === undefined || value === null) {
      return;
    } else if (Array.isArray(value)) {
      if (value.length === 0) return;
      entry = value.join(',');
    } else if (typeof value === 'object') {
      if (size(value) === 0) return;
      entry = JSON.stringify(value);
    } else {
      entry = `${value}`;
    }

    newParams[key] = entry;
  });
  // Avoid setting query param if they are null or undefined
  const queryParams = new URLSearchParams(newParams);
  const stringifiedQueryParams = queryParams.toString();
  return stringifiedQueryParams ? `?${stringifiedQueryParams}` : '';
};

type ParsedParams<K extends string, V = string> = Record<
  K[number],
  V | undefined
>;

export function useParsedSearchParams<K extends string>(
  ...keys: ReadonlyArray<K>
): ParsedParams<K> {
  const params = useSearchParams();
  const parsed = useMemo(
    () =>
      keys.reduce(
        (m, k) => ({ ...m, [k]: params.get(k) ?? undefined }),
        {} as ParsedParams<K>
      ),
    [keys, params]
  );

  return parsed;
}

export function useRedirectWithParams() {
  const search = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const prevParams = useMemo(() => {
    const result: Record<string, QueryParam> = {};
    search.forEach((value, key) => {
      result[key] = value;
    });
    return result;
  }, [search]);

  const isMounted = useIsMounted();

  // Create debounced function using useMemo
  const debouncedRedirect = useMemo(
    () =>
      debounce(
        (
          params?: Record<string, QueryParam>,
          path?: string,
          scroll?: boolean
        ) => {
          const newParams = {
            ...prevParams,
            ...params,
          };
          const newParamsString = stringifyQueryParams(newParams);
          const newPath = path || pathname;

          if (!isMounted()) return;

          if (path) {
            router.push(`${newPath}${newParamsString}`, { scroll });
          } else {
            router.replace(`${newPath}${newParamsString}`, { scroll });
          }
        },
        100
      ),
    [prevParams, pathname, router, isMounted]
  );

  // Wrap the debounced function in useCallback
  const redirectWithParams = useCallback(
    ({
      params,
      path,
      scroll,
    }: {
      params?: Record<string, QueryParam>;
      path?: string;
      scroll?: boolean;
    }) => {
      debouncedRedirect(params, path, scroll);
    },
    [debouncedRedirect]
  );

  return redirectWithParams;
}
