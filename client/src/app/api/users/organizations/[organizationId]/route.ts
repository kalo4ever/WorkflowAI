// eslint-disable-next-line no-restricted-imports
import { clerkClient } from '@clerk/nextjs/server';
import { captureException } from '@sentry/nextjs';
import LRUCache from 'lru-cache';
import { NextRequest, NextResponse } from 'next/server';

export type OrganizationInformation = {
  id: string;
  name: string;
  imageUrl: string | undefined;
};

const organizationCache = new LRUCache<string, OrganizationInformation>({
  max: 1000,
  ttl: 1000 * 60 * 60 * 24, // 24 hours
});

export const GET = async (
  req: NextRequest,
  { params }: { params: { organizationId: string } }
) => {
  const { organizationId } = params;

  if (!organizationId) {
    return new NextResponse('organizationId is required', { status: 400 });
  }
  if (typeof organizationId !== 'string') {
    return new NextResponse('organizationId must be a string', { status: 400 });
  }

  if (!process.env.CLERK_SECRET_KEY) {
    return new NextResponse('CLERK_SECRET_KEY is not set', { status: 500 });
  }

  // Check if the organization is in the cache
  const cachedOrganization = organizationCache.get(organizationId);
  if (!!cachedOrganization) {
    return NextResponse.json(cachedOrganization);
  }

  // If not in cache, fetch the organization from Clerk
  try {
    const organization = await clerkClient.organizations.getOrganization({
      organizationId: organizationId,
    });

    const organizationInfo: OrganizationInformation = {
      id: organization.id,
      name: organization.name,
      imageUrl: organization.imageUrl,
    };

    organizationCache.set(organizationId, organizationInfo);

    return NextResponse.json(organizationInfo);
  } catch (error) {
    captureException(error, {
      tags: { organizationId },
      extra: { context: 'Fetching organization from Clerk' },
    });
    return new NextResponse('Error fetching organization data from Clerk', {
      status: 500,
    });
  }
};
