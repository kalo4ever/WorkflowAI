'use client';

import React, { useEffect, useRef, useState } from 'react';
import { LandingPageContainer } from './container/LandingPageContainer';
import { CompliantInformationSection } from './sections/CompliantInformationSection';
import { HeaderSection } from './sections/HeaderSection';
import { InvestorLogosSection } from './sections/InvestorLogosSection';
import { PriceSection } from './sections/PriceSection';
import { SectionSeparator } from './sections/SectionSeparator';
import { StickyHeader } from './sections/SickyHeader';
import { SuggestedFeaturesSection } from './sections/SuggestedFeatures/SuggestedFeaturesSection';
import { VideoEntry, VideosSection } from './sections/VideosSection';

const videos: VideoEntry[] = [
  {
    title: 'Build new AI features without writing code, in a few minutes',
    description:
      'WorkflowAI empowers product managers to create powerful AI features entirely through an intuitive web interface—no coding required.',
    videoId: '88ea7f2de6647fa4e051378c218a4938',
    quote:
      '“I always have ideas for great AI features, but getting engineering resources used to be a huge bottleneck. WorkflowAI lets me build and ship new AI-driven features myself—no coding, no waiting.”',
    authorImageSrc: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/author1.jpg',
    quoteAuthor: 'Perri Gould',
    authorsPosition: 'Head of product',
    authorsCompany: 'Berry Street',
    companyURL: 'https://www.berrystreet.co',
  },
  {
    title: 'Compare all models side-by-side',
    description:
      'Use the playground to compare between over 60 different models, all available without any setup. Pay the same price as using directly from the AI provider.',
    videoId: '435cef8dd99a0174311e01ae4d343f18',
    quote:
      '“Before WorkflowAI, we were locked into OpenAI because integrating other models was too complex. Now, switching is effortless—we’ve easily tested alternatives and saved over 90% by using Google’s models.”',
    authorImageSrc: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/author2.jpg',
    quoteAuthor: 'Maxime Germain',
    authorsPosition: 'CEO',
    authorsCompany: 'InterfaceAI',
    companyURL: 'https://interfaceai.com',
  },
  {
    title: 'Understand and improve your AI features in production.',
    description:
      'WorkflowAI automatically logs all outputs, making it easy to diagnose issues and refine prompts for better performance.',
    videoId: 'c118e79228b019f3d95228bbf236b563',
    quote:
      '“AI is non-deterministic, so understanding what happens after deployment is crucial. WorkflowAI automatically logs all outputs, enabling rapid issue diagnosis and prompt improvements.”',
    authorImageSrc: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/author3.jpg',
    quoteAuthor: 'Gabriela Garcia',
    authorsPosition: 'Product Manager',
    authorsCompany: 'Luni',
    companyURL: 'https://www.luni.app',
  },
  {
    title: 'Integration that makes your engineering team happy',
    description:
      'WorkflowAI provides your engineering team with a seamless, developer-friendly integration process, turning AI features built by PMs into production-ready experiences quickly.',
    videoId: 'f3c737f08a3a0f5da10d90bffd3441a6',
    quote:
      '“When PMs build new AI features using WorkflowAI, integrating them is straightforward and stress-free. Our engineers appreciate how quickly these features fit into our existing backend—without surprises.”',
    authorImageSrc: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/author4.jpg',
    quoteAuthor: 'Aymeric Beaumet',
    authorsPosition: 'CTO',
    authorsCompany: 'InterfaceAI',
    companyURL: 'https://interfaceai.com',
  },
  {
    title: 'Get the best prompt engineer in your team',
    description: 'WorkflowAI can automatically re-write prompts based on your feedback.',
    videoId: 'f0347bc39b9b0557006a0428538215d9',
    quote:
      '“Manually writing prompts feels outdated. With WorkflowAI’s Prompt Engineer, we’ve significantly improved prompt quality—delivering more accurate and reliable AI features”.',
    authorImageSrc: 'https://workflowai.blob.core.windows.net/workflowai-public/landing/author5.jpg',
    quoteAuthor: 'Antoine Martin',
    authorsPosition: 'CEO',
    authorsCompany: 'Amo',
    companyURL: 'https://amo.co',
  },
];

type LandingPageProps = {
  companyURL?: string;
};

export function LandingPage(props: LandingPageProps) {
  const { companyURL } = props;

  const scrollToPricing = () => {
    const pricingSection = document.getElementById('pricing');
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollRef = useRef<HTMLDivElement>(null);
  const secondStickyHeaderRef = useRef<HTMLDivElement>(null);

  const [isSecondHeaderAboveViewport, setIsSecondHeaderAboveViewport] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (secondStickyHeaderRef.current && scrollRef.current) {
        const rect = secondStickyHeaderRef.current.getBoundingClientRect();
        const containerRect = scrollRef.current.getBoundingClientRect();
        setIsSecondHeaderAboveViewport(rect.bottom < containerRect.top);
      }
    };

    const element = scrollRef.current;
    element?.addEventListener('scroll', handleScroll);
    return () => element?.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <LandingPageContainer scrollToPricing={scrollToPricing} scrollRef={scrollRef}>
      <HeaderSection className='sm:mt-28 mt-24' scrollToPricing={scrollToPricing} />
      <SuggestedFeaturesSection className='mt-16 mb-32' companyURL={companyURL} />
      <div className='text-center text-gray-900 sm:text-[36px] text-[32px] sm:font-medium font-semibold'>
        Explore WorkflowAI as a...
      </div>
      <div className='h-[1px] w-[1px]' ref={secondStickyHeaderRef} />
      <div className='sticky top-0 z-10 w-full'>
        <StickyHeader
          firstOption='Product Manager'
          secondOption='Software Engineer'
          showBackground={isSecondHeaderAboveViewport}
          makeTransparent={false}
        />
      </div>
      <VideosSection videos={videos} className='mt-[80px] sm:mb-[144px] mb-[64px]' />
      <SectionSeparator id='pricing' />
      <PriceSection className='sm:mt-[104px] mt-[64px]' />
      <CompliantInformationSection className='mt-10 mb-16' />
      <SectionSeparator />
      <InvestorLogosSection className='mt-16 mb-28 py-10' />
    </LandingPageContainer>
  );
}
