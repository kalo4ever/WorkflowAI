// eslint-disable-next-line no-restricted-imports
import { type User, clerkClient } from '@clerk/nextjs/server';
import { captureException } from '@sentry/nextjs';
import LRUCache from 'lru-cache';
import { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

// Create an LRU cache with a maximum of 1000 items that expire after 24 hours
const userCache = new LRUCache<string, User>({
  max: 1000,
  ttl: 1000 * 60 * 60 * 24, // 24 hours
});

export const GET = async (
  req: NextRequest,
  { params }: { params: { userId: string } }
) => {
  const { userId } = params;

  if (!userId) {
    return new NextResponse('userId is required', { status: 400 });
  }
  if (typeof userId !== 'string') {
    return new NextResponse('userId must be a string', { status: 400 });
  }

  if (!process.env.CLERK_SECRET_KEY) {
    return new NextResponse('CLERK_SECRET_KEY is not set', { status: 500 });
  }

  // Check if the user is in the cache
  const cachedUser = userCache.get(userId);
  if (cachedUser) {
    return NextResponse.json(cachedUser);
  }

  // If not in cache, fetch the user from Clerk
  try {
    const user = await clerkClient.users.getUser(userId);

    // Store the user in the cache
    userCache.set(userId, user);

    return NextResponse.json(user);
  } catch (error) {
    captureException(error, {
      tags: { userId },
      extra: { context: 'Fetching user from Clerk' },
    });
    return new NextResponse('Error fetching user data from Clerk', {
      status: 500,
    });
  }
};
