import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

type Props = {
  showSuggestedFeaturesModal: () => void;
  className?: string;
  routeForSignUp: string;
};

export function HeaderComponent(props: Props) {
  const { className, showSuggestedFeaturesModal, routeForSignUp } = props;

  return (
    <div className={cn('flex flex-col items-center sm:px-16 px-4 w-full max-w-[1260px]', className)}>
      <div className='sm:text-[60px] text-[48px] text-gray-900 font-semibold text-center leading-[1.1]'>
        Build AI features your users will love.
      </div>
      <div className='sm:text-[20px] text-[18px] text-gray-500 font-normal text-center leading-[1.5] max-w-[740px] mt-4'>
        WorkflowAI is an open-source platform where product and engineering teams collaborate to build and iterate on AI
        features.
      </div>
      <div className='flex sm:flex-row flex-col sm:w-fit w-full gap-4 my-4 items-center justify-center'>
        <Button variant='newDesign' className='sm:w-fit w-full' onClick={showSuggestedFeaturesModal}>
          Try demo
        </Button>
        <Button variant='newDesignIndigo' toRoute={routeForSignUp} className='sm:w-fit w-full'>
          Start building for free
        </Button>
      </div>
    </div>
  );
}

type URLHeaderComponentProps = {
  className?: string;
};

export function URLHeaderComponent(props: URLHeaderComponentProps) {
  const { className } = props;

  return (
    <div className={cn('flex flex-col items-center sm:px-16 px-4 w-full max-w-[1260px]', className)}>
      <div className='sm:text-[60px] text-[48px] text-gray-900 font-semibold text-center leading-[1.1]'>
        Build AI features your users will love.
      </div>
      <div className='sm:text-[20px] text-[18px] text-gray-500 font-normal text-center leading-[1.5] max-w-[750px] mt-4'>
        WorkflowAI is an open-source platform where product and engineering teams collaborate to build and iterate on AI
        features.
      </div>
      <div className='flex sm:flex-row flex-col sm:w-fit w-full gap-4 my-10 items-center justify-center'>
        <Button variant='newDesignIndigo' className='sm:w-fit w-full' toRoute='/'>
          Learn more about WorkflowAI
        </Button>
      </div>
    </div>
  );
}
