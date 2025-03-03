'use client';

import { LandingPageContainer } from './LandingPageContainer';
import { HeaderSection } from './sections/HeaderSection';
import { InvestorLogosSection } from './sections/InvestorLogosSection';
import { URLEntrySection } from './sections/URLEntrySection';
import { VideoSection } from './sections/VideoSection';

export function LandingPage() {
  return (
    <LandingPageContainer>
      <HeaderSection className='mt-28' />
      <URLEntrySection className='mt-16' />
      <InvestorLogosSection className='mt-20' />
      <VideoSection className='mt-20' />
    </LandingPageContainer>
  );
}
