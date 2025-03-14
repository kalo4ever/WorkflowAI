import { useRouter } from 'next/navigation';
import { PropsWithChildren } from 'react';
import { Loader } from '@/components/ui/Loader';
import { useAuth } from '@/lib/AuthContext';
import { useTenantID } from '@/lib/hooks/useTaskParams';
import { TENANT_PLACEHOLDER, replaceTenant } from '@/lib/routeFormatter';
import { useOrganizationBySlug } from '@/store/organization_by_slug';
import { TenantID } from '@/types/aliases';

function RedirectIfNeeded(props: PropsWithChildren<{ urlTenant: TenantID }>) {
  const { urlTenant } = props;
  const { replace } = useRouter();

  const { organization, isInitialized } = useOrganizationBySlug(urlTenant);

  if (!isInitialized) {
    return <Loader centered />;
  }

  if (organization === undefined || organization.slug === undefined) {
    // Until we are sure that all organizations have been migrated,
    // the safest thing to do is to return the children
    return props.children;
  }

  if (urlTenant !== organization.slug) {
    const currentURL = window.location.href;
    replace(replaceTenant(currentURL, urlTenant, organization.slug));
    return null;
  }

  return props.children;
}

export function RedirectForTenant(props: PropsWithChildren) {
  const { children } = props;
  const urlTenant = useTenantID();

  const { isLoaded: isAuthLoaded, tenantSlug } = useAuth();

  // We wait until the user and organization are loaded to check if the user needs to be redirected
  if (!isAuthLoaded) {
    return <Loader centered />;
  }

  // As a shortcut, all personal organization will use "_" as the URL tenant. We could replace with a slug of the user
  // email for example
  if (urlTenant === TENANT_PLACEHOLDER) {
    return props.children;
  }

  // When the url tenant is the same as the user tenant, we don't need to redirect or
  // check the server data
  if (tenantSlug === urlTenant) {
    return props.children;
  }

  return <RedirectIfNeeded urlTenant={urlTenant}>{children}</RedirectIfNeeded>;
}
