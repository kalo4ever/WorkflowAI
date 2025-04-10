'use client';

import { useCallback, useState } from 'react';
import { Dialog } from '@/components/ui/Dialog';
import { DialogContent } from '@/components/ui/Dialog';
import { signUpRoute } from '@/lib/routeFormatter';
import { useOrFetchUptime } from '@/store/fetchers';
import { LandingPageContainer } from './container/LandingPageContainer';
import { CompaniesMoneyComponent } from './sections/Components/CompaniesMoneyComponent';
import { ComparisionComponent } from './sections/Components/ComparisionComponent';
import { GraphComponent } from './sections/Components/GraphComponent';
import { GridComponent } from './sections/Components/GridComponent';
import { HeaderComponent } from './sections/Components/HeaderComponent';
import { ImageComponent } from './sections/Components/ImageComponent';
import { InvestorLogosComponent } from './sections/Components/InvestorLogosComponent';
import { PriceComponent } from './sections/Components/PriceComponent';
import { QuoteComponent } from './sections/Components/QuoteComponent';
import { RowsComponent } from './sections/Components/RowsComponent';
import { SubheaderComponent } from './sections/Components/SubheaderComponent';
import { VideoDemoComponent } from './sections/Components/VideoDemoComponent';
import * as LandingStaticData from './sections/StaticData/LandingStaticData';
import { SuggestedFeaturesComponentModal } from './sections/SuggestedFeatures/SuggestedFeaturesComponent';

export function LandingPage() {
  const [companyURL, setCompanyURL] = useState<string | undefined>(undefined);
  const [showSuggestedFeaturesModal, setShowSuggestedFeaturesModal] = useState<boolean>(false);

  const routeForSignUp = signUpRoute();

  const { workflowUptime, openaiUptime } = useOrFetchUptime();

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
        showSuggestedFeaturesModal={() => setShowSuggestedFeaturesModal(true)}
        routeForSignUp={routeForSignUp}
      />
      <VideoDemoComponent className='sm:mt-20 mt-14' />

      <CompaniesMoneyComponent className='sm:mt-40 mt-28' />

      <SubheaderComponent entry={LandingStaticData.eighteenthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={LandingStaticData.eighteenthNewImageEntry} className='mt-12' />

      <SubheaderComponent entry={LandingStaticData.seventeenthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={LandingStaticData.seventeenthNewImageEntry} className='mt-12' />

      <SubheaderComponent entry={LandingStaticData.sixteenthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={LandingStaticData.sixteenthNewImageEntry} className='mt-12' />

      <SubheaderComponent entry={LandingStaticData.fifteenthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={LandingStaticData.fifteenthNewImageEntry} className='mt-12' />

      <SubheaderComponent entry={LandingStaticData.fourteenthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={LandingStaticData.fourteenthNewImageEntry} className='mt-12' />

      <SubheaderComponent entry={LandingStaticData.thirteenthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={LandingStaticData.thirteenthNewImageEntry} className='mt-12' />

      <SubheaderComponent entry={LandingStaticData.twelfthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <GridComponent
        entries={LandingStaticData.twelfthNewFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />

      <SubheaderComponent entry={LandingStaticData.eleventhNewHeaderEntry} className='sm:mt-40 mt-28' />
      <GridComponent
        entries={LandingStaticData.eleventhNewFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />

      <RowsComponent entries={LandingStaticData.tenthNewFeaturesEntries} className='sm:mt-40 mt-28' />
      <QuoteComponent entry={LandingStaticData.tenthNewQuoteEntry} className='mt-12' />

      <GridComponent
        entries={LandingStaticData.ninthNewFeaturesEntries}
        className='sm:mt-40 mt-28'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />

      <SubheaderComponent entry={LandingStaticData.eighthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <ImageComponent entry={LandingStaticData.eighthNewImageEntry} className='mt-12' />

      <SubheaderComponent entry={LandingStaticData.seventhNewHeaderEntry} className='sm:mt-40 mt-28' id='pricing' />
      <PriceComponent className='mt-12' />
      <QuoteComponent entry={LandingStaticData.seventhNewQuoteEntry} className='mt-12' />

      <SubheaderComponent entry={LandingStaticData.sixthNewHeaderEntry} className='sm:mt-20 mt-12' />

      <SubheaderComponent entry={LandingStaticData.fifthNewHeaderEntry} className='sm:mt-20 mt-12' />
      <GridComponent entries={LandingStaticData.fifthNewFeaturesEntries} className='mt-12' showThreeColumns />

      <SubheaderComponent entry={LandingStaticData.fourthNewHeaderEntry} className='sm:mt-40 mt-28' />
      <GridComponent entries={LandingStaticData.fourthNewFeaturesEntries} className='mt-12' showThreeColumns />

      <SubheaderComponent entry={LandingStaticData.thirdNewHeaderEntry} className='sm:mt-20 mt-12' />

      <SubheaderComponent entry={LandingStaticData.comparisionHeaderEntry} className='sm:mt-20 mt-12' />
      <ComparisionComponent className='mt-12' workflowUptime={workflowUptime} openaiUptime={openaiUptime} />
      <GraphComponent className='mt-32 sm:mt-20' workflowUptime={workflowUptime} />

      <SubheaderComponent entry={LandingStaticData.secondNewHeaderEntry} className='sm:mt-40 mt-28' />
      <GridComponent
        entries={LandingStaticData.secondNewFeaturesEntries}
        className='mt-12'
        scrollToSuggestedFeatures={scrollToSuggestedFeatures}
      />

      <InvestorLogosComponent className='sm:mt-40 mt-28' />

      <SubheaderComponent
        entry={LandingStaticData.firstNewFeaturesEntries}
        className='sm:mt-40 mt-28 sm:mb-40 mb-28'
        routeForSignUp={routeForSignUp}
      />

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
