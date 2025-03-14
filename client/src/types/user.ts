export interface User {
  id: string;
  email?: string;
  firstName?: string;
  lastName?: string;
  imageUrl?: string;
  fullName?: string;
  username?: string;
}

// Not using Clerk UserResource since it definies a bunch of other stuff
// we don't need. Boilerplate is for mapping nulls to undefined
type ClerkUser = {
  id: string;
  firstName?: string | null;
  lastName?: string | null;
  imageUrl?: string | null;
  fullName?: string | null;
  primaryEmailAddress?: {
    emailAddress: string;
  } | null;
  username?: string | null;
};
export function clerkUserToUser(user: ClerkUser): User {
  return {
    id: user.id,
    email: user.primaryEmailAddress?.emailAddress,
    firstName: user.firstName ?? undefined,
    lastName: user.lastName ?? undefined,
    imageUrl: user.imageUrl ?? undefined,
    fullName: user.fullName ?? undefined,
    username: user.username ?? undefined,
  };
}
