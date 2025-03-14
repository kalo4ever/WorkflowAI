import { NextResponse } from 'next/server';
import { export_public_key } from '@/lib/token/token';

export const dynamic = 'force-dynamic';

export const GET = async () => {
  const publicKey = await export_public_key();

  return new NextResponse(
    JSON.stringify({
      keys: [{ ...publicKey, id: '1' }],
    }),
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );
};
