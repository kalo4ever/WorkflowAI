import { cn } from '@/lib/utils';

type SectionSeparatorProps = {
  className?: string;
  id?: string;
};

export function SectionSeparator(props: SectionSeparatorProps) {
  const { className, id } = props;

  return (
    <div className={cn('flex flex-col gap-6 items-center px-16 w-full max-w-[1132px]', className)} id={id}>
      <div className='flex w-full h-[1px] bg-gray-100' />
    </div>
  );
}
