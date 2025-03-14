import { ChevronRight } from 'lucide-react';
import { signUpRoute } from '@/lib/routeFormatter';

export function LoggedOutBanner() {
  return (
    <div className='w-full h-[44px] bg-slate-900 text-white flex items-center justify-center gap-4 text-sm'>
      <div>Start building with WorkflowAI</div>
      <a href='/' className='flex items-center'>
        <div>Start Building</div>
        <ChevronRight size={16} />
      </a>
    </div>
  );
}

type LoggedOutBannerForDemoTaskProps = {
  name: string | undefined;
};

export function LoggedOutBannerForDemoTask(
  props: LoggedOutBannerForDemoTaskProps
) {
  const route = signUpRoute();
  const { name } = props;
  return (
    <div className='w-full h-[44px] bg-slate-900 text-white flex items-center justify-center gap-4'>
      <div className='text-gray-200 font-normal text-[13px]'>
        You’re viewing a preview of {name} AI Agent
      </div>
      <a href={route} className='flex items-center'>
        <div className='text-white text-[14px] font-medium'>
          Create account to unlock all features
        </div>
        <ChevronRight size={16} />
      </a>
    </div>
  );
}
