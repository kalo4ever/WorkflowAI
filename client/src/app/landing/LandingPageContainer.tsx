import { People16Filled } from '@fluentui/react-icons';
import Image from 'next/image';
import GitHubSrc from '@/components/Images/GitHubIcon.png';
import { WorkflowAIIcon } from '@/components/Logos/WorkflowAIIcon';
import { Button } from '@/components/ui/Button';
import { ExtendedBordersContainer } from '@/components/v2/ExtendedBordersContainer';
import { useAuth } from '@/lib/AuthContext';
import { useDefaultRedirectRoute } from '@/lib/hooks/useTaskParams';
import { PATHS, signInRoute, signUpRoute } from '@/lib/routeFormatter';

type LandingPageContainerProps = {
  children: React.ReactNode;
};

export function LandingPageContainer(props: LandingPageContainerProps) {
  const { children } = props;

  const { isSignedIn: isLogged } = useAuth();

  const routeForSignUp = signUpRoute();
  const routeForSignIn = signInRoute();
  const dashboardRoute = useDefaultRedirectRoute(PATHS.SIGNIN);

  return (
    <div className='flex flex-col h-full w-full font-lato p-6'>
      <ExtendedBordersContainer
        className='flex flex-col h-full w-full'
        borderColor='gray-100'
        margin={24}
      >
        <div className='flex items-center justify-between gap-2 h-[60px] px-4 flex-shrink-0 border-b border-gray-100'>
          <Button variant='text' size='none' toRoute={'/'}>
            <div className='flex items-center gap-2 flex-shrink-0'>
              <WorkflowAIIcon ratio={1.3} />
              <span className='font-sans text-[20px] bg-gradient-to-r from-[#8759E3] to-[#4235F8] text-transparent bg-clip-text'>
                <span className='font-semibold'>Workflow</span>
                <span className='font-normal'>AI</span>
              </span>
            </div>
          </Button>

          <div className='flex flex-row gap-2 items-center'>
            <Button
              variant='newDesignText'
              toRoute='mailto:team@workflowai.support'
            >
              Contact Us
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
        </div>
        <div className='flex h-[calc(100%-60px)] w-full flex-col items-center overflow-y-auto landing-scroll-container'>
          {children}
        </div>
      </ExtendedBordersContainer>
    </div>
  );
}
