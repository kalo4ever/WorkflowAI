import { isEqual } from 'lodash';
import { useRef } from 'react';

// TODO: test
export const useStableValue = <T>(instableValue: T) => {
  const stableValue = useRef<T>(instableValue);

  if (!isEqual(instableValue, stableValue.current)) {
    stableValue.current = instableValue;
  }

  return stableValue.current;
};
