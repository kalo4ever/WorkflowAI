import { Checkmark12Filled } from '@fluentui/react-icons';
import Image from 'next/image';
import GitHubSrc from '@/components/Images/GitHubIcon.png';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/lib/AuthContext';
import { signUpRoute } from '@/lib/routeFormatter';
import { cn } from '@/lib/utils';

type HeaderEntryProps = {
  text: string;
  href?: string;
  onClick?: () => void;
};

function HeaderEntry(props: HeaderEntryProps) {
  const { text, href, onClick } = props;

  return (
    <div className='flex flex-row gap-[6px] items-center'>
      <Checkmark12Filled className='text-gray-700' />
      <a
        href={href}
        className='text-[16px] text-gray-500 font-normal underline cursor-pointer'
        target='_blank'
        onClick={onClick}
      >
        {text}
      </a>
    </div>
  );
}

type HeaderSectionProps = {
  scrollToPricing: () => void;
  className?: string;
};

export function HeaderSection(props: HeaderSectionProps) {
  const { className, scrollToPricing } = props;

  const { isSignedIn: isLogged } = useAuth();

  const routeForSignUp = signUpRoute();

  return (
    <div className={cn('flex flex-col items-center px-16 w-full max-w-[1260px]', className)}>
      <div className='text-[60px] text-gray-900 font-semibold text-center leading-[1.1]'>
        Go from idea to AI-powered feature—in minutes
      </div>
      <div className='text-[24px] text-gray-500 font-normal text-center leading-[1.5] max-w-[860px] mt-4'>
        WorkflowAI makes it easy for product managers and software engineers to quickly build, test, and deploy their
        first reliable AI features, without requiring deep AI knowledge or extensive coding.
      </div>
      <div className='flex flex-wrap gap-4 mt-4'>
        <HeaderEntry text='Open-Source (deploy anywhere)' href='https://github.com/workflowai/workflowai' />
        <HeaderEntry text='Compatible with any backend' href='https://docs.workflowai.com/' />
        <HeaderEntry text='No markup from AI providers' onClick={scrollToPricing} />
      </div>
      <div className='flex flex-row gap-5 mt-16'>
        {!isLogged && (
          <Button variant='newDesignIndigo' toRoute={routeForSignUp}>
            Try for free
          </Button>
        )}
        <Button
          variant='newDesignGray'
          icon={<Image src={GitHubSrc} alt='GitHub' className='w-4 h-4' />}
          toRoute='https://github.com/WorkflowAI/workflowai'
          target='_blank'
          rel='noopener noreferrer'
        >
          Star on Github
        </Button>
      </div>
    </div>
  );
}
