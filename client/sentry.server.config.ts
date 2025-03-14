// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  enabled:
    process.env.NODE_ENV === 'production' &&
    // We don't rely on the presence of the DSN to make disabling explicit
    process.env.SENTRY_DISABLED !== 'true',

  environment:
    process.env.NEXT_PUBLIC_ENV_NAME || process.env.ENV_NAME || 'unknown',

  // Adjust this value in production, or use tracesSampler for greater control
  tracesSampleRate: 0.1,

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: false,

  replaysOnErrorSampleRate: 1.0,

  replaysSessionSampleRate: 0.05,
});
