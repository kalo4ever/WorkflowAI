// eslint-disable-next-line no-restricted-imports
import { auth as clerkAuth, currentUser as clerkCurrentUser } from '@clerk/nextjs/server';
import LRUCache from 'lru-cache';
import { User, clerkUserToUser } from '@/types/user';
import { getTenantSlug } from './auth_utils';
import { DISABLE_AUTHENTICATION, HARDCODED_TENANT } from './constants';

interface AuthResult {
  userId?: string | null;
  orgSlug?: string | null;
  orgId?: string | null;
  redirectToSignIn: (options: { returnBackUrl: string }) => null;
}

// LRU Cache for user data to avoid hitting the Clerk API
// This is annoying but needed until we use straight clerk tokens
const userDataCache = new LRUCache<string, User>({
  max: 1000,
  // Caching for 5 minutes
  // We could probably go higher since we don't use highly mutable data
  // (email, username).
  ttl: 1000 * 60 * 5, // 5 min
});

export function auth(): AuthResult {
  if (DISABLE_AUTHENTICATION) {
    return {
      orgSlug: HARDCODED_TENANT,
      orgId: HARDCODED_TENANT,
      redirectToSignIn: () => null,
    };
  }
  return clerkAuth();
}

export async function currentUser(userId?: string | null): Promise<User | null> {
  if (DISABLE_AUTHENTICATION) {
    return { id: '1' };
  }
  if (userId) {
    const cachedUser = userDataCache.get(userId);
    if (cachedUser) {
      return cachedUser;
    }
  }
  const clerkUser = await clerkCurrentUser();
  if (!clerkUser) {
    return null;
  }
  const converted = clerkUserToUser(clerkUser);
  userDataCache.set(converted.id, converted);
  return converted;
}

export async function tenantSlug(): Promise<string | undefined> {
  const authResult = auth();
  if (!authResult) {
    return undefined;
  }
  const user = await currentUser(authResult.userId);
  if (!user) {
    return undefined;
  }
  return getTenantSlug({ slug: authResult.orgSlug }, user);
}
