'use client';

import * as amplitude from '@amplitude/analytics-browser';
import { sessionReplayPlugin } from '@amplitude/plugin-session-replay-browser';
import { captureException } from '@sentry/nextjs';
import { ReactNode, useEffect } from 'react';
import { useAuth } from '../../lib/AuthContext';

interface AmplitudeConfiguratorProps {
  children: ReactNode;
}

export function AmplitudeConfigurator(props: AmplitudeConfiguratorProps) {
  const { children } = props;
  const { tenantSlug } = useAuth();
  const environment = process.env.NEXT_PUBLIC_ENV_NAME;

  useEffect(() => {
    const apiKey = process.env.NEXT_PUBLIC_AMPLITUDE_API_KEY;

    if (typeof window === 'undefined' || !apiKey) {
      const message = !apiKey
        ? `Amplitude API key not found`
        : `Window object not found`;
      captureException(`Amplitude not initialized: ${message}`);
      return;
    }

    amplitude.init(apiKey);

    const sessionReplayTracking = sessionReplayPlugin({
      sampleRate: 1.0,
    });
    amplitude.add(sessionReplayTracking);

    if (environment) {
      const identify = new amplitude.Identify();
      identify.set('environment', environment);
      amplitude.identify(identify);
    }
  }, [environment]);

  useEffect(() => {
    if (tenantSlug) {
      amplitude.setUserId(tenantSlug);

      if (environment) {
        const identify = new amplitude.Identify();
        identify.set('environment', environment);
        amplitude.identify(identify);
      }
    }
  }, [environment, tenantSlug]);

  return <>{children}</>;
}
