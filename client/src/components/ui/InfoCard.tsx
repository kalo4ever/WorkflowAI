import { Info, LucideIcon, X } from 'lucide-react';

type InfoCardProps = {
  title?: string;
  content?: string;
  lucideIcon?: LucideIcon;
  onClose?: () => void;
};

export function InfoCard(props: InfoCardProps) {
  const { title, content, lucideIcon: Icon = Info, onClose } = props;
  return (
    <div className='w-full flex items-center gap-4 p-4 border border-purple-200 rounded-xl bg-purple-50 text-purple-700'>
      <Icon size={24} className='shrink-0' />
      <div className='flex flex-col gap-1'>
        {title && <div>{title}</div>}
        {content && <div className='text-sm'>{content}</div>}
      </div>
      {onClose && (
        <X size={24} className='cursor-pointer shrink-0' onClick={onClose} />
      )}
    </div>
  );
}
