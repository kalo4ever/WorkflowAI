import { captureException } from '@sentry/nextjs';
import { NextResponse } from 'next/server';
import { RequestError } from '@/lib/api/client';
import { API_URL } from '@/lib/constants';

export const GET = async () => {
  // Try and contact the API client

  try {
    const res = await fetch(`${API_URL}/probes/readiness`, {
      cache: 'no-cache',
    });
    if (!res.ok && res.status !== 503) {
      captureException(new RequestError(res.status, 'probes/readiness', res));
      return new NextResponse('not ready', { status: 500 });
    }
  } catch (error: unknown) {
    captureException(error);
    return new NextResponse('not ready', { status: 500 });
  }

  return new NextResponse('ready', { status: 200 });
};
