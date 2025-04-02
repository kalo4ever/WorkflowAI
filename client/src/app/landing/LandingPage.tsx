'use client';

import { useCallback, useState } from 'react';
import { Dialog } from '@/components/ui/Dialog';
import { DialogContent } from '@/components/ui/Dialog';
import { LandingPageContainer } from './container/LandingPageContainer';
import { GirdComponent } from './sections/Components/GirdComponent';
import { HeaderComponent } from './sections/Components/HeaderComponent';
import { ImageComponent } from './sections/Components/ImageComponent';
import { InvestorLogosComponent } from './sections/Components/InvestorLogosComponent';
import { PriceComponent } from './sections/Components/PriceComponent';
import { QuoteComponent } from './sections/Components/QuoteComponent';
import { RowsComponent } from './sections/Components/RowsComponent';
import { SubheaderComponent } from './sections/Components/SubheaderComponent';
import { VideoDemoComponent } from './sections/Components/VideoDemoComponent';
import {
  eighthHeaderEntry,
  eighthImageEntry,
  eighthQuoteEntry,
  eleventhFeaturesEntries,
  eleventhHeaderEntry,
  eleventhQuoteEntry,
  fifthHeaderEntry,
  fifthQuoteEntry,
  firstFeaturesEntries,
  firstHeaderEntry,
  firstQuoteEntry,
  fourthFeaturesEntries,
  fourthHeaderEntry,
  ninthFeaturesEntries,
  ninthHeaderEntry,
  ninthQuoteEntry,
  secondFeaturesEntries,
  secondQuoteEntry,
  seventhFeaturesEntries,
  seventhHeaderEntry,
  seventhQuoteEntry,
  sixthHeaderEntry,
  sixthImageEntry,
  sixthQuoteEntry,
  tenthFeaturesEntries,
  thirdHeaderEntry,
  thirdImageEntry,
  thirdQuoteEntry,
  thirteenthHeaderEntry,
  twelfthFeaturesEntries,
} from './sections/StaticData/LandingStaticData';
import {
  SuggestedFeaturesComponent,
  SuggestedFeaturesComponentModal,
} from './sections/SuggestedFeatures/SuggestedFeaturesComponent';

export function LandingPage() {
  const [companyURL, setCompanyURL] = useState<string | undefined>(undefined);
  const [showSuggestedFeaturesModal, setShowSuggestedFeaturesModal] = useState<boolean>(false);

  const scrollToPricing = useCallback(() => {
    const pricingSection = document.getElementById('pricing');
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  const scrollToSuggestedFeatures = useCallback(() => {
    const suggestedFeaturesSection = document.getElementById('suggested-features');
    if (suggestedFeaturesSection) {
      suggestedFeaturesSection.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  return (
    <LandingPageContainer scrollToPricing={scrollToPricing}>
      <HeaderComponent
        className='mt-20'
        scrollToPricing={scrollToPricing}
        showSuggestedFeaturesModal={() => setShowSuggestedFeaturesModal(true)}
      />
      <VideoDemoComponent className='sm:mt-20 mt-14' />
      <InvestorLogosComponent className='mt-20' />

      <SubheaderComponent entry={firstHeaderEntry} className='sm:mt-40 mt-28' />
      <GirdComponent
        entries={firstFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />
      <QuoteComponent entry={firstQuoteEntry} className='mt-12' />

      <RowsComponent entries={secondFeaturesEntries} className='sm:mt-40 mt-28' />
      <QuoteComponent entry={secondQuoteEntry} className='mt-12' />

      <SubheaderComponent entry={thirdHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={thirdImageEntry} className='mt-12' />
      <QuoteComponent entry={thirdQuoteEntry} className='mt-12' />

      <SubheaderComponent entry={fourthHeaderEntry} className='sm:mt-40 mt-28' />
      <GirdComponent
        entries={fourthFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />

      <SubheaderComponent entry={fifthHeaderEntry} className='sm:mt-40 mt-28' id='pricing' />
      <PriceComponent className='mt-12' />
      <QuoteComponent entry={fifthQuoteEntry} className='mt-12' />

      <SubheaderComponent entry={sixthHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={sixthImageEntry} className='mt-12' />
      <QuoteComponent entry={sixthQuoteEntry} className='mt-12' />

      <SubheaderComponent entry={seventhHeaderEntry} className='sm:mt-40 mt-28' />
      <GirdComponent
        entries={seventhFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />
      <QuoteComponent entry={seventhQuoteEntry} className='mt-12' />

      <SubheaderComponent entry={eighthHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={eighthImageEntry} className='mt-12' />
      <QuoteComponent entry={eighthQuoteEntry} className='mt-12' />

      <SubheaderComponent entry={ninthHeaderEntry} className='sm:mt-40 mt-28' />
      <GirdComponent
        entries={ninthFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />
      <QuoteComponent entry={ninthQuoteEntry} className='mt-12' />

      <GirdComponent
        entries={tenthFeaturesEntries}
        className='sm:mt-40 mt-28'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />

      <SubheaderComponent entry={eleventhHeaderEntry} className='sm:mt-40 mt-28' />
      <GirdComponent
        entries={eleventhFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />
      <QuoteComponent entry={eleventhQuoteEntry} className='mt-12' />

      <GirdComponent
        entries={twelfthFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />

      <SubheaderComponent entry={thirteenthHeaderEntry} className='sm:mt-40 mt-28' id='suggested-features' />
      <SuggestedFeaturesComponent className='mt-12 mb-28' companyURL={companyURL} setCompanyURL={setCompanyURL} />

      <Dialog open={showSuggestedFeaturesModal} onOpenChange={() => setShowSuggestedFeaturesModal(false)}>
        <DialogContent className='sm:min-w-[90vw] sm:h-[90vh] h-full min-w-full p-0'>
          <SuggestedFeaturesComponentModal
            companyURL={companyURL}
            setCompanyURL={setCompanyURL}
            onClose={() => setShowSuggestedFeaturesModal(false)}
          />
        </DialogContent>
      </Dialog>
    </LandingPageContainer>
  );
}
