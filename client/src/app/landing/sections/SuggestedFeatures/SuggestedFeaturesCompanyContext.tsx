import { PlaceholderRectangle } from './PlaceholderRectangle';

type Props = {
  companyContext: string | undefined;
  isLoading: boolean;
};

export function SuggestedFeaturesCompanyContext(props: Props) {
  const { companyContext, isLoading } = props;

  if (isLoading && !companyContext) {
    return (
      <div className='text-gray-500 text-[13px] font-normal px-4 py-3 rounded-[2px] bg-gray-50 flex w-full'>
        <div className='flex flex-col gap-2 animate-pulse w-full'>
          <PlaceholderRectangle className='w-[100%] h-[14px]' />
          <PlaceholderRectangle className='w-[100%] h-[14px]' />
          <PlaceholderRectangle className='w-[100%] h-[14px]' />
        </div>
      </div>
    );
  }

  return (
    <div className='text-gray-500 text-[13px] font-normal px-4 py-3 rounded-[2px] bg-gray-50 whitespace-pre-line break-words overflow-y-auto max-h-[190px]'>
      {companyContext}
    </div>
  );
}
