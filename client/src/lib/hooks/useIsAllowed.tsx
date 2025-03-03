import { useCallback } from 'react';
import { displayErrorToaster } from '@/components/ui/Sonner';
import { useAuth } from '@/lib/AuthContext';
import { useDefaultRedirectRoute } from '@/lib/hooks/useTaskParams';
import { useRedirectWithParams } from '@/lib/queryString';
import { PATHS } from '@/lib/routeFormatter';
import { useIsSameTenant } from './useTaskParams';

export function useIsAllowed() {
  const { isSignedIn } = useAuth();
  const isSameTenant = useIsSameTenant();
  const signUpRoute = useDefaultRedirectRoute(PATHS.SIGNUP);
  const redirectWithParams = useRedirectWithParams();

  const checkIfSignedIn = useCallback(
    (displayModal = true) => {
      if (!isSignedIn) {
        if (displayModal) {
          redirectWithParams({
            path: signUpRoute,
            params: {},
          });
        }
        return false;
      }

      return true;
    },
    [isSignedIn, redirectWithParams, signUpRoute]
  );

  const checkIfAllowed = useCallback(
    (displayToaster = true) => {
      if (!checkIfSignedIn(displayToaster)) {
        return false;
      }

      if (!isSameTenant) {
        if (displayToaster) {
          displayErrorToaster(
            'This AI agent does not belong to you',
            'Action blocked:'
          );
        }
        return false;
      }

      return true;
    },
    [checkIfSignedIn, isSameTenant]
  );

  return {
    checkIfSignedIn,
    checkIfAllowed,
  };
}
