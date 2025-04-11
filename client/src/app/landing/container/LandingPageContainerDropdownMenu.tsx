import { NavigationFilled } from '@fluentui/react-icons';
import Image from 'next/image';
import GitHubSrc from '@/components/Images/GitHubIcon.png';
import { Button } from '@/components/ui/Button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger } from '@/components/ui/DropdownMenu';

type LandingPageContainerDropdownMenuProps = {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  scrollToPricing: () => void;
  isLogged: boolean;
  routeForSignIn: string;
  routeForSignUp: string;
  dashboardRoute: string;
};
export function LandingPageContainerDropdownMenu(props: LandingPageContainerDropdownMenuProps) {
  const { isOpen, setIsOpen, scrollToPricing, isLogged, routeForSignIn, routeForSignUp, dashboardRoute } = props;

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant='newDesignGray' icon={<NavigationFilled className='h-4 w-4' />} className='w-9 h-9 p-0' />
      </DropdownMenuTrigger>
      <DropdownMenuContent align='end' className='w-[250px] flex flex-col gap-2 p-2'>
        <Button variant='newDesignText' toRoute='mailto:team@workflowai.support' className='w-full justify-start pl-1'>
          Contact
        </Button>
        <Button variant='newDesignText' onClick={scrollToPricing} className='w-full justify-start pl-2'>
          Pricing
        </Button>
        <Button
          variant='newDesignText'
          toRoute='https://github.com/WorkflowAI/WorkflowAI/discussions'
          className='w-full justify-start text-gray-700 hover:text-gray-700 hover:opacity-80 pl-1'
        >
          Join our Community on GitHub
        </Button>
        <Button
          variant='newDesignText'
          toRoute='https://docs.workflowai.com/'
          target='_blank'
          rel='noopener noreferrer'
          className='w-full justify-start pl-1'
        >
          Documentation
        </Button>
        <Button
          variant='newDesignGray'
          icon={<Image src={GitHubSrc} alt='GitHub' className='w-4 h-4' />}
          toRoute='https://github.com/WorkflowAI/workflowai'
          target='_blank'
          rel='noopener noreferrer'
          className='w-full justify-center cursor-pointer'
        >
          Star on GitHub
        </Button>
        {isLogged ? (
          <Button variant='newDesign' toRoute={dashboardRoute} className='w-full justify-center cursor-pointer'>
            Dashboard
          </Button>
        ) : (
          <>
            <Button variant='newDesign' toRoute={routeForSignIn} className='w-full justify-center cursor-pointer'>
              Login
            </Button>
            <Button variant='newDesignIndigo' toRoute={routeForSignUp} className='w-full justify-center cursor-pointer'>
              Sign up
            </Button>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
