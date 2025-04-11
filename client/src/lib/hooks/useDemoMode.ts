import { useAuth } from '@/lib/AuthContext';
import { useTenantID } from './useTaskParams';

export function useDemoMode() {
  const { isSignedIn, tenantSlug } = useAuth();
  const tenant = useTenantID();

  const isLoggedOut = !isSignedIn;
  const onDifferentTenant = tenant !== tenantSlug && tenant !== '_';
  const isInDemoMode = isLoggedOut || onDifferentTenant;

  return { isInDemoMode, isLoggedOut, onDifferentTenant };
}
