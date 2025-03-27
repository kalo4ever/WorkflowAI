'use client';

/* eslint-disable no-restricted-imports */
import { CreateOrganization } from '@clerk/nextjs';
import { OrganizationResource } from '@clerk/types';
import { tasksRoute } from '@/lib/routeFormatter';
import { TenantID } from '@/types/aliases';

function postSelectOrganizationURL(org: OrganizationResource) {
  return tasksRoute(org.slug as TenantID);
}
export default function OrganizationCreatePage() {
  return (
    <div className='w-full h-full flex items-center justify-center'>
      <CreateOrganization afterCreateOrganizationUrl={postSelectOrganizationURL} skipInvitationScreen={false} />
    </div>
  );
}
