import { captureMessage } from '@sentry/nextjs';
import { KeyLike, SignJWT, exportJWK, importPKCS8 } from 'jose';
import { CookieStore } from '@/types/cookies';
import { auth, currentUser } from '../auth';
import { getTenantSlug } from '../auth_utils';
import { UNKNOWN_USER_ID_COOKIE_NAME } from '../constants';
import { setAnonUserIdCookie } from './anon';

// functions are only available in the server

const alg = 'ES256';

export async function parse_sign_key(key = process.env.WORKFLOWAI_API_SIGN_KEY) {
  if (!key) {
    throw new Error('API_SIGN_KEY is not set');
  }
  const decoded = Buffer.from(key, 'base64').toString('utf-8');

  return await importPKCS8(decoded, alg);
}

let cached_sign_key: KeyLike | null = null;

async function cache_sign_key() {
  if (cached_sign_key === null) {
    cached_sign_key = await parse_sign_key();
  }
  return cached_sign_key;
}

interface Claims {
  [propName: string]: unknown;

  sub: string;
}

export async function build_api_jwt(claims: Claims, expiration: string = '60d', sign_key?: KeyLike) {
  const key = sign_key ?? (await cache_sign_key());

  const jwt = await new SignJWT(claims)
    // TODO: set kid
    .setProtectedHeader({ alg })
    .setIssuedAt()
    // really long expiration time for now
    .setExpirationTime(expiration)
    .sign(key);

  return jwt;
}

export type TokenData = {
  [key: string]: unknown;
  // userId is as provided by clerk
  userId?: string;
  // orgId is as provided by clerk
  orgId?: string;
  // orgSlug is as provided by clerk
  orgSlug?: string;
  // email is used to compute the deprecated tenant
  email?: string;
  // unknownUserId is only set for unknown users, aka when the user is not logged in
  unknownUserId?: string;
};

function token_data_to_claim({ email, orgId, orgSlug, unknownUserId, userId }: TokenData): Claims {
  return {
    orgId,
    // @ts-expect-error we check that at least one is provided above
    sub: email ?? orgId,
    orgSlug,
    userId,
    unknownUserId,
  };
}

export async function build_api_jwt_for_tenant(token_data: TokenData, expiration: string = '365d', signKey?: KeyLike) {
  return await build_api_jwt(token_data_to_claim(token_data), expiration, signKey);
}

export function extract_claim_from_jwt(jwt: string): TokenData | undefined {
  const claims = jwt.split('.')[1];
  if (!claims) {
    return undefined;
  }
  const decoded = Buffer.from(claims, 'base64').toString('utf-8');
  const parsed = JSON.parse(decoded);
  return parsed as TokenData;
}

export function check_jwt_for_tenant(jwt: string, token_data: TokenData) {
  // Check that the JWT sub is the given email
  // The signature is not checked

  const parsed = extract_claim_from_jwt(jwt);
  if (parsed === undefined) {
    return false;
  }
  const expected_claims = token_data_to_claim(token_data);

  for (const key in expected_claims) {
    if (parsed[key] !== expected_claims[key]) {
      return false;
    }
  }
}

export async function export_public_key(sign_key?: KeyLike) {
  const key = sign_key ?? (await cache_sign_key());

  const out = await exportJWK(key);
  delete out.d;
  return out;
}

export async function getAuthenticatedTokenData(): Promise<TokenData | undefined> {
  const user = await currentUser();
  const { orgSlug, orgId } = auth();
  const email = user?.email;

  if (!orgId && !email) {
    return undefined;
  }

  return {
    orgId: orgId ?? undefined,
    // TODO: this should match the getTenantSlug function in ClerkLoader.tsx
    // We should find a better way to ensure the match
    orgSlug: getTenantSlug({ slug: orgSlug }, user),
    email,
    userId: user?.id,
  };
}

export function getTokenDataForUnknownUser(unknownUserId: string): TokenData {
  return {
    unknownUserId,
  };
}

export function getOrSetUnknownUserId(cookieStore: CookieStore) {
  // First try and find the unknownUserId in the cookies
  const unknownUserId = cookieStore.get(UNKNOWN_USER_ID_COOKIE_NAME);
  if (unknownUserId && !!unknownUserId.value) {
    return unknownUserId.value;
  }
  // If there is a token with an unknownUserId, return that
  const token = cookieStore.get('x-api-token');
  if (token) {
    const tokenData = extract_claim_from_jwt(token.value);
    if (tokenData?.unknownUserId) {
      return tokenData.unknownUserId;
    }
    // We could capture a message on sentry here as it would be unexpected
    // but since we do not clear the x-api-token when a user logs out
    // we would get a lot of spam.
    // The safest way to proceed is to generate a new unknownUserId,
    // the existing x-api-token will be invalidated by check_jwt_for_tenant
    console.warn('x-api-token with no unknownUserId when generating an unknownUserId', {
      tokenData,
    });
  }

  // This should not happen. Cookie should be generated client side to avoid race conditions
  captureMessage('generating new unknownUserId', {
    level: 'warning',
    extra: {
      token,
    },
  });

  return setAnonUserIdCookie(cookieStore);
}

export async function buildTokenData(cookieStore: CookieStore) {
  // First try to get token data from clerk if the user is logged in
  const tokenData = await getAuthenticatedTokenData();
  if (tokenData) {
    return tokenData;
  }

  // Otherwise we generate a token for an anonymous user
  const unknownUserId = getOrSetUnknownUserId(cookieStore);
  return getTokenDataForUnknownUser(unknownUserId);
}
