'use client';

import { WorkflowAIIcon } from '@/components/Logos/WorkflowAIIcon';
import { Button } from '@/components/ui/Button';
import { ExtendedBordersContainer } from '@/components/v2/ExtendedBordersContainer';
import { useAuth } from '@/lib/AuthContext';
import { useIsMobile } from '@/lib/hooks/useIsMobile';
import { useDefaultRedirectRoute } from '@/lib/hooks/useTaskParams';
import { PATHS, signInRoute, signUpRoute } from '@/lib/routeFormatter';
import { LandingPageContainerButtons } from './LandingPageContainerButtons';

type LandingPageContainerProps = {
  scrollToPricing: () => void;
  children: React.ReactNode;
  scrollRef?: React.RefObject<HTMLDivElement>;
};

export function LandingPageContainer(props: LandingPageContainerProps) {
  const { children, scrollToPricing, scrollRef } = props;

  const { isSignedIn: isLogged } = useAuth();

  const routeForSignUp = signUpRoute();
  const routeForSignIn = signInRoute();
  const dashboardRoute = useDefaultRedirectRoute(PATHS.SIGNIN);

  const isMobile = useIsMobile();

  return (
    <div className='flex flex-col h-full w-full font-lato px-0 sm:px-6 py-6 bg-custom-gradient-1'>
      <ExtendedBordersContainer
        className='flex flex-col h-full w-full'
        borderColor='gray-100'
        margin={isMobile ? 0 : 24}
      >
        <div className='flex items-center justify-between gap-2 h-[60px] px-4 w-full border-b border-gray-100'>
          <Button variant='text' size='none' toRoute={'/'} className='flex-shrink-0'>
            <div className='flex items-center gap-2'>
              <WorkflowAIIcon ratio={1.3} />
              <span className='font-sans text-[20px] bg-gradient-to-r from-[#8759E3] to-[#4235F8] text-transparent bg-clip-text'>
                <span className='font-semibold'>Workflow</span>
                <span className='font-normal'>AI</span>
              </span>
            </div>
          </Button>

          <div className='flex flex-1 justify-end min-w-0'>
            <LandingPageContainerButtons
              scrollToPricing={scrollToPricing}
              isLogged={isLogged}
              routeForSignIn={routeForSignIn}
              routeForSignUp={routeForSignUp}
              dashboardRoute={dashboardRoute}
            />
          </div>
        </div>
        <div
          className='flex h-[calc(100%-60px)] w-full flex-col items-center overflow-y-auto overflow-x-hidden landing-scroll-container'
          ref={scrollRef}
        >
          {children}
        </div>
      </ExtendedBordersContainer>
    </div>
  );
}
