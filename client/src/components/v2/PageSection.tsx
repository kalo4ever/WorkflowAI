import { cn } from '@/lib/utils';

type PageSectionProps = {
  title: string;
  children?: React.ReactNode;
  showTopBorder?: boolean;
};

export function PageSection(props: PageSectionProps) {
  const { title, children, showTopBorder = false } = props;
  return (
    <div
      className={cn(
        'flex flex-row w-full justify-between items-center border-dashed border-gray-200 border-b',
        showTopBorder && 'border-t border-dashed border-gray-200'
      )}
    >
      <div className='text-base font-semibold text-gray-700 px-4 py-3 capitalize'>{title}</div>
      <div className='flex flex-row gap-2 pr-4'>{children}</div>
    </div>
  );
}
