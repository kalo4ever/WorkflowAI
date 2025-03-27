'use client';

/* eslint-disable no-restricted-imports */
import { OrganizationList } from '@clerk/nextjs';
import { OrganizationResource, UserResource } from '@clerk/types';
import { getTenantSlug } from '@/lib/auth_utils';
import { tasksRoute } from '@/lib/routeFormatter';
import { TenantID } from '@/types/aliases';
import { clerkUserToUser } from '@/types/user';

function postSelectOrganizationURL(org: OrganizationResource) {
  return tasksRoute(org.slug as TenantID);
}

function postSelectPersonalURL(user: UserResource) {
  return tasksRoute(getTenantSlug(undefined, clerkUserToUser(user)) as TenantID);
}

export default function OrganizationSelectPage() {
  return (
    <div className='w-full h-full flex items-center justify-center'>
      <OrganizationList
        afterSelectOrganizationUrl={postSelectOrganizationURL}
        afterSelectPersonalUrl={postSelectPersonalURL}
      />
    </div>
  );
}
