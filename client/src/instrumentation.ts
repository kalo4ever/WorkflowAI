import * as Sentry from '@sentry/nextjs';

async function registerSentry() {
  if (process.env.SENTRY_DISABLED === 'true') {
    return;
  }
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('../sentry.server.config');
  }
}

export async function register() {
  await registerSentry();
}

export const onRequestError = Sentry.captureRequestError;
