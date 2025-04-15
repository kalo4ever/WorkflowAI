import { CookieOptions, CookieStore } from '@/types/cookies';
import { UNKNOWN_USER_ID_COOKIE_NAME } from '../constants';

export function anonUserIdCookieProps(): CookieOptions {
  return {
    maxAge: 60 * 60 * 24 * 30 * 12, // almost 1 year
    path: '/',
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    httpOnly: false,
  };
}

export function setAnonUserIdCookie(cookieStore: CookieStore) {
  const newUnknownUserId = crypto.randomUUID();
  cookieStore.set(UNKNOWN_USER_ID_COOKIE_NAME, newUnknownUserId, anonUserIdCookieProps());
  return newUnknownUserId;
}
