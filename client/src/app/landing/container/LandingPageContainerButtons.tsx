import { People16Filled } from '@fluentui/react-icons';
import Image from 'next/image';
import { useEffect, useRef, useState } from 'react';
import GitHubSrc from '@/components/Images/GitHubIcon.png';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { LandingPageContainerDropdownMenu } from './LandingPageContainerDropdownMenu';

type LandingPageContainerButtonsProps = {
  scrollToPricing: () => void;
  isLogged: boolean;
  routeForSignIn: string;
  routeForSignUp: string;
  dashboardRoute: string;
};

export function LandingPageContainerButtons(props: LandingPageContainerButtonsProps) {
  const { scrollToPricing, isLogged, routeForSignIn, routeForSignUp, dashboardRoute } = props;
  const [showMenu, setShowMenu] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const buttonsRef = useRef<HTMLDivElement>(null);

  const checkWidth = () => {
    if (containerRef.current && buttonsRef.current) {
      const containerWidth = containerRef.current.getBoundingClientRect().width;
      const buttonsWidth = buttonsRef.current.getBoundingClientRect().width;
      const shouldShowMenu = buttonsWidth > containerWidth;
      setShowMenu(shouldShowMenu);
    }
  };

  useEffect(() => {
    checkWidth();

    // Create a ResizeObserver to watch for size changes
    const resizeObserver = new ResizeObserver(checkWidth);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    // Also listen for window resize events
    window.addEventListener('resize', checkWidth);

    return () => {
      window.removeEventListener('resize', checkWidth);
      resizeObserver.disconnect();
    };
  }, []);

  return (
    <div ref={containerRef} className='flex flex-row gap-2 items-center justify-end min-w-0 relative'>
      <div
        ref={buttonsRef}
        className={cn(
          'flex flex-row gap-2 items-center transition-opacity duration-200',
          showMenu ? 'opacity-0 pointer-events-none' : 'opacity-100'
        )}
      >
        <Button variant='newDesignText' toRoute='mailto:team@workflowai.support'>
          Contact
        </Button>
        <Button variant='newDesignText' onClick={scrollToPricing}>
          Pricing
        </Button>
        <Button
          variant='newDesignText'
          toRoute='https://github.com/WorkflowAI/WorkflowAI/discussions'
          icon={<People16Filled className='w-4 h-4 text-gray-700' />}
          className='text-gray-700 hover:text-gray-700 hover:opacity-80'
        >
          Join our Community on GitHub
        </Button>
        <Button
          variant='newDesignText'
          toRoute='https://docs.workflowai.com/'
          target='_blank'
          rel='noopener noreferrer'
        >
          Documentation
        </Button>
        <Button
          variant='newDesignGray'
          icon={<Image src={GitHubSrc} alt='GitHub' className='w-4 h-4' />}
          toRoute='https://github.com/WorkflowAI/workflowai'
          target='_blank'
          rel='noopener noreferrer'
        >
          Star on Github
        </Button>
        {isLogged ? (
          <Button variant='newDesign' toRoute={dashboardRoute}>
            Dashboard
          </Button>
        ) : (
          <>
            <Button variant='newDesign' toRoute={routeForSignIn}>
              Login
            </Button>
            <Button variant='newDesignIndigo' toRoute={routeForSignUp}>
              Sign up
            </Button>
          </>
        )}
      </div>
      <div
        className={cn(
          'absolute right-0 top-0 transition-opacity duration-200',
          showMenu ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
      >
        <LandingPageContainerDropdownMenu
          isOpen={isOpen}
          setIsOpen={setIsOpen}
          scrollToPricing={scrollToPricing}
          isLogged={isLogged}
          routeForSignIn={routeForSignIn}
          routeForSignUp={routeForSignUp}
          dashboardRoute={dashboardRoute}
        />
      </div>
    </div>
  );
}
