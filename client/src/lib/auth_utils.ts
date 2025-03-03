import type { User } from '@/types/user';
import { HARDCODED_TENANT } from './constants';

function slugify(str: string) {
  str = str.toLowerCase().trim();
  str = str.replace(/\s+/g, '-'); // Replace spaces with hyphens
  str = str.replace(/[^\w-]+/g, ''); // Remove non-alphanumeric characters except hyphens
  return str;
}

function slugFromUser(user: User) {
  if (user.username) {
    return user.username;
  }
  if (user.email) {
    return slugify(user.email);
  }
  return undefined;
}

// A prefix to distinguish user slugs from organization slugs
export const USER_SLUG_PREFIX = '@';

export function getTenantSlug(
  organization: { slug: string | null | undefined } | null | undefined,
  user: User | null | undefined
) {
  if (organization && organization.slug) {
    return organization.slug;
  }
  if (HARDCODED_TENANT) {
    return HARDCODED_TENANT;
  }
  if (user) {
    const userSlug = slugFromUser(user);
    if (userSlug) {
      // When the slug is from a user we always prefix so that it can be recognized as a user slug
      return USER_SLUG_PREFIX + userSlug;
    }
  }
  return undefined;
}
