import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import { buildTokenData, build_api_jwt_for_tenant } from '@/lib/token/token';

export const GET = async () => {
  const tokenData = await buildTokenData(cookies());

  const jwt = await build_api_jwt_for_tenant(tokenData, '1m');

  return new NextResponse(JSON.stringify({ token: jwt }), {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};
