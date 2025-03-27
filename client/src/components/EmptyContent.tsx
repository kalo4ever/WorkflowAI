import { Button } from './ui/Button';

type EmptyContentProps = {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  buttonText?: string;
  onButtonClick?: () => void;
  href?: string;
};

export function EmptyContent(props: EmptyContentProps) {
  const { icon, title, subtitle, buttonText, onButtonClick, href } = props;
  return (
    <div className='flex flex-col items-center justify-center h-full w-full mb-8'>
      <div className='flex items-center justify-center w-[64px] h-[64px] rounded-full bg-gray-100 mb-6'>{icon}</div>
      <div className='text-gray-700 text-[14px] font-semibold'>{title}</div>
      <div className='text-gray-500 text-[14px] font-normal'>{subtitle}</div>
      {buttonText && (onButtonClick || href) && (
        <Button
          variant='newDesign'
          onClick={onButtonClick}
          className='mt-4'
          target={href ? '_blank' : undefined}
          toRoute={href}
        >
          {buttonText}
        </Button>
      )}
    </div>
  );
}
