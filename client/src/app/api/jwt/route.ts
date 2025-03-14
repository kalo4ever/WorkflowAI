import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';
import { buildTokenData, build_api_jwt_for_tenant } from '@/lib/token/token';

export const GET = async (request: NextRequest) => {
  const cookieStore = cookies();
  const tokenData = await buildTokenData(cookieStore);
  const queryParams = request.nextUrl.searchParams;
  const userID = queryParams.get('userID');

  if (userID || tokenData.userId) {
    if (userID !== tokenData.userId) {
      throw new Error('User ID mismatch');
    }
  }

  const jwt = await build_api_jwt_for_tenant(
    tokenData,
    !tokenData.unknownUserId ? '3650d' : '15m'
  );

  return new NextResponse(JSON.stringify({ token: jwt }), {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};
