import * as amplitude from '@amplitude/analytics-browser';
import { useCallback } from 'react';

export function useOpenedTypeformTracker() {
  return useCallback(() => {
    const sourceURL = window.location.href;
    amplitude.track('user.opened.typeform', { source_URL: sourceURL });
  }, []);
}
