'use server';

import { cookies } from 'next/headers';
import { CookieStore } from '@/types/cookies';
import { BACKEND_API_URL } from '../constants';
import { TokenData, buildTokenData, build_api_jwt_for_tenant, check_jwt_for_tenant } from '../token/token';

async function getOrSetToken(data: TokenData, cookieStore: CookieStore, setCookie = false) {
  const token = cookieStore.get('x-api-token');
  if (token && check_jwt_for_tenant(token.value, data)) {
    return token.value;
  }
  const newToken = await build_api_jwt_for_tenant(data);
  if (newToken && setCookie) {
    cookieStore.set('x-api-token', newToken, {
      maxAge: 60 * 60 * 24 * 30,
      path: '/',
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      httpOnly: false,
    });
  }
  return newToken;
}

export async function serverFetch(path: string, inits: RequestInit, setCookie: boolean) {
  const cookieStore = cookies();

  const tokenData = await buildTokenData(cookieStore);
  const apiToken = await getOrSetToken(tokenData, cookieStore, setCookie);

  inits.headers = {
    Authorization: `Bearer ${apiToken}`,
    'Content-Type': 'application/json',
    'x-workflowai-source': 'web',
    'x-workflowai-version': process.env.NEXT_PUBLIC_RELEASE_NAME ?? 'unknown',
    ...(inits.headers ?? {}),
  };

  const response = await fetch(`${BACKEND_API_URL}${path}`, inits);
  return response;
}
